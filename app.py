import streamlit as st
from pawpal_system import Pet, Owner, Task, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialisation — runs only on the very first load.
# After that, Streamlit reuses the existing objects instead of recreating them.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # Owner object, created when the form is submitted

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.header("1. Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "How many minutes do you have today?", min_value=10, max_value=480, value=90, step=10
    )
    preference = st.text_input("Any scheduling preference? (optional)", placeholder="e.g. no tasks before 9am")
    submitted = st.form_submit_button("Save owner")

if submitted:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    if preference:
        st.session_state.owner.add_preference(preference)
    st.success(f"Owner saved: {st.session_state.owner}")

# Guard — nothing below makes sense without an owner
if st.session_state.owner is None:
    st.info("Fill in your owner info above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2 — Add pets
# ---------------------------------------------------------------------------
st.divider()
st.header("2. Add a Pet")

with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["cat", "dog", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    notes = st.text_input("Special notes (optional)", placeholder="e.g. needs morning meds")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    pet = Pet(name=pet_name, species=species, age=int(age), notes=notes)
    owner.add_pet(pet)
    st.success(f"Added: {pet}")

if owner.pets:
    st.write("**Current pets:**", ", ".join(str(p) for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")
    st.stop()

# ---------------------------------------------------------------------------
# Section 3 — Add tasks to a pet
# ---------------------------------------------------------------------------
st.divider()
st.header("3. Add Tasks")

pet_names = [p.name for p in owner.pets]

with st.form("task_form"):
    selected_pet_name = st.selectbox("Which pet?", pet_names)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"])
    with col4:
        frequency = st.selectbox("Frequency", ["daily", "weekly"])
    add_task = st.form_submit_button("Add task")

if add_task:
    target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
    target_pet.add_task(Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        frequency=frequency,
    ))
    st.success(f"Added '{task_title}' to {selected_pet_name}.")

for pet in owner.pets:
    if pet.tasks:
        st.write(f"**{pet.name}'s tasks:**")
        st.table([
            {"Task": t.title, "Duration (min)": t.duration_minutes,
             "Priority": t.priority, "Frequency": t.frequency, "Status": "done" if t.completed else "pending"}
            for t in pet.tasks
        ])

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("4. Today's Schedule")

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("No pending tasks found. Add some tasks above first.")
    else:
        schedule = Schedule(owner=owner, start_time="08:00")
        schedule.generate()
        st.code(schedule.explain(), language=None)
