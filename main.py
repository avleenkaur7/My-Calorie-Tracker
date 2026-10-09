
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from charts import nutrient_chart
from storage import load_food_log, save_food_log

columns = [
    "Date", "Food", "Quantity", "Unit",
    "Calories", "Proteins", "Carbs", "Fat", "Fibre"
]

if "food_log" not in st.session_state:
    st.session_state.food_log = load_food_log()

st.title("Count before you eat")

# Box 1: Personal details
with st.container(border=True):
    st.subheader("Your Details")

    gender = st.radio(
        "Select your gender",
        ["Female", "Male"],
        horizontal=True
    )
    
    if "previous_gender" not in st.session_state:
        st.session_state.previous_gender = gender

    elif st.session_state.previous_gender != gender:
        st.session_state.food_log = pd.DataFrame(columns=columns)


    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age (years)", min_value=1,
            max_value=120, value=21
        )
        weight = st.number_input(
            "Weight (kg)", min_value=1.0,
            value=52.0, step=0.5
        )

    with col2:
        height = st.number_input(
            "Height (cm)", min_value=50.0,
            max_value=250.0, value=166.0, step=0.5
        )
    
    activity = st.selectbox(
        "Activity Level",
        [
            "Sedentary",
            "Lightly active",
            "Moderately active",
            "Very active"
        ]
    )
      
    # Calculate BMR using the Mifflin-St Jeor equation
    if gender == "Female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    activity_factors = {
        "Sedentary": 1.2,
        "Lightly active": 1.375,
        "Moderately active": 1.55,
        "Very active": 1.725
    }

    daily_target = int(bmr * activity_factors[activity])

# Box 2: Food and nutrients
with st.container(border=True):
    st.subheader("Track Food")
    
    st.metric("Daily Calorie Target", f"{daily_target} kcal")

    food = st.selectbox(
        "Select food",
        ["Select a food", "Egg", "Banana", "Oats", "Chicken",
 "Roti", "Dal", "Milk", "Paneer"]
    )

    if food in ["Egg", "Banana","Roti"]:
        quantity = st.number_input(
            "Quantity (pieces)",
            min_value=1, value=1, step=1
        )
    else:
        quantity = st.number_input(
            "Quantity (grams)",
            min_value=1, value=100, step=1
        )
    
    # Nutritional values per piece or per 100g
   
    food_data = pd.DataFrame({
        "Food": [
            "Egg", "Banana", "Oats", "Chicken",
            "Roti", "Dal", "Milk", "Paneer"
        ],
        "Calories": [72, 105, 389, 165, 120, 116, 61, 265],
        "Proteins": [6.3, 1.3, 16.9, 31, 3.5, 9, 3.2, 18.3],
        "Carbs": [0.4, 27, 66.3, 0, 20, 20, 4.8, 1.2],
        "Fat": [4.8, 0.4, 6.9, 3.6, 3, 0.4, 3.3, 20.8],
        "Fibre": [0, 3.1, 10.6, 0, 3, 7.9, 0, 0]
    })
   

   
    nutrient_columns = [
        "Calories", "Proteins", "Carbs", "Fat", "Fibre"
    ]

    if food == "Select a food":
        nutrients = {name: 0 for name in nutrient_columns}
    else:
        food_row = food_data.loc[food_data["Food"] == food]

        base_values = food_row[nutrient_columns].iloc[0].to_numpy()

        multiplier = (
            quantity
            if food in ["Egg", "Banana", "Roti"]
            else quantity / 100
        )

        calculated_values = base_values * multiplier

        nutrients = dict(zip(nutrient_columns, calculated_values))


        st.metric(
        "Current Food Calories",
        f"{nutrients['Calories']:.0f} kcal"
    )
    nutrient_targets = {
            "Proteins": 50,
            "Carbs": 300,
            "Fat": 70,
            "Fibre": 25
        }
    st.subheader("Selected Food — Nutrients")

    for name in ["Proteins", "Carbs", "Fat", "Fibre"]:
        st.write(f"{name}: {nutrients[name]:.1f} g")
        st.progress(
            min(float(nutrients[name]) / nutrient_targets[name], 1.0)
        )

    if st.button("Add Food"):
        if food == "Select a food":
            st.warning("Please select a food first.")
        else:
            unit = "pieces" if food in ["Egg", "Banana","Roti"] else "g"

            
            new_entry = pd.DataFrame([{
                "Date": pd.Timestamp.today().strftime("%Y-%m-%d"),
                "Food": food,
                "Quantity": quantity,
                "Unit": unit,
                "Calories": nutrients["Calories"],
                "Proteins": nutrients["Proteins"],
                "Carbs": nutrients["Carbs"],
                "Fat": nutrients["Fat"],
                "Fibre": nutrients["Fibre"]
            }])

            st.session_state.food_log = pd.concat(
                [st.session_state.food_log, new_entry],
                ignore_index=True
            )

            save_food_log(st.session_state.food_log)

            st.success(f"{food} added!")

          
       
    
    
   
    nutrient_columns = [
        "Calories", "Proteins", "Carbs", "Fat", "Fibre"
    ]
    st.subheader("Your Food History")
    
    st.dataframe(
        st.session_state.food_log,
        use_container_width=True,
        hide_index=True
    )
    totals = st.session_state.food_log[
        nutrient_columns
    ].sum()

    total_calories = totals["Calories"]


    st.metric(
        "Total Calories Consumed",
        f"{total_calories:.0f} kcal"
    )

    st.progress(
        min(total_calories / daily_target, 1.0)
    )

    st.write(
        f"{total_calories:.0f} / {daily_target} kcal consumed"
    )

 
   
    nutrient_names = ["Proteins", "Carbs", "Fat", "Fibre"]

    target_values = np.array([
        nutrient_targets[name] for name in nutrient_names
    ])

    consumed_values = np.array([
        totals[name] for name in nutrient_names
    ])

    progress_values = np.clip(
        consumed_values / target_values, 0, 1
    )

    for i, name in enumerate(nutrient_names):
        st.write(f"{name}: {consumed_values[i]:.1f} g")
        st.progress(float(progress_values[i]))
st.pyplot(nutrient_chart(totals))