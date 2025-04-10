import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar
from search import RecipeEmbeddingSearch  # Importing the class from search.py
from search import AzureOpenAIChat
st.markdown('<h1 style="color: #FF5A5F;"> 😋 Meal Genie</h1>', unsafe_allow_html=True)




container = st.container(border=False)
with container:
    keywords = st_tags(
    label='Enter Ingredients you have',
        text='Enter ingredient and press enter',
        #value=["Carrots", "Onion"],
        #suggestions=['five', 'six', 'seven', 'eight', 'nine', 'three', 'eleven', 'ten', 'four'],
        maxtags=18,
        key="aljnf")
    ingredients = list(keywords)
    ingredients_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
    for ingredient in ingredients:
        ingredients_html += f'<div style="background-color: #F0F2F6; padding: 5px 10px; border-radius: 15px;">{ingredient}</div>'

    #container.markdown(ingredients_html, unsafe_allow_html=True)


col1, col2 = st.columns(2,gap="medium", border=False)


# color3 = col3.select_slider(
#     "Fat",
#     options=[
#         "Low",
#         "Medium",
#         "High",
#     ]
# )


cuisine_options = ["Indian", "Dutch"]
cuisine = col1.selectbox("Select Cuisine", cuisine_options)
col1.write("") 

time_options = ["10-15 mins", "15-30 mins", "30+ mins"]
time = col1.pills("Cooking Time", time_options, selection_mode="single")

protein = col2.select_slider(
    "Protein",
    options=[
        "Low",
        "Medium",
        "High",
        
    ]
)


carb = col2.select_slider(
    "Carbs",
    options=[
         "Low",
        "Medium",
        "High",
    ]
)




# options = ["<500 KCal", "<1000 KCal", "No Limits"]
# selection = col2.pills("Calories", options, selection_mode="single")
#left, right = st.columns(2,vertical_alignment="center", gap="small", border=True)
# col1, col2 = st.columns(2,gap="small", border=True)



if st.button("Generate Recipes!", use_container_width=True, type="primary"):

    search_queries = {
            "ingredients": ingredients,
    }
# Pass this search query to your LLM or API (Here we are just displaying it for now)
    pinecone_api_key = st.secrets["pinecone"]["api_key"]
    whisper_api_key = st.secrets["whisper"]["api_key"]

    recipe_search = RecipeEmbeddingSearch(
    
          index_name="recipe-embeddings",

            azure_endpoint="https://access-01.openai.azure.com",



                
            pinecone_api_key=st.secrets["pinecone"]["api_key"],

            deployment_name="text-embedding-3-large",
            
            api_key = st.secrets["whisper"]["api_key"],
            api_version="2023-05-15"
    )
   

   # st.write("Searching for recipes with the following ingredients:", search_queries)
    #query = " ".join(ingredients)
    query = " AND ".join(ingredients)
    #st.write(query)
    
    similar_recipes = recipe_search.search_similar_recipes(query)
    
    if similar_recipes:
             # Collecting the recipe information for the LLM
           recipe_info = "\n".join([f"Recipe {i+1}: {recipe.get('recipe_name')}, "
                                 f"Description: {recipe.get('recipe_text')}"
                                 for i, recipe in enumerate(similar_recipes)])
           #st.write(recipe_info)
            #for i, recipe in enumerate(similar_recipes, 1):
    #                 st.write(f"\nResult {i}:")
    #                 st.write(f"Recipe Name: {recipe['recipe_name']}")
    #                 st.write(f"Similarity Score: {recipe['score']:.4f}")
    #                 #text_preview = recipe['recipe_text'][:500] + "..." if len(recipe['recipe_text']) > 500 else recipe['recipe_text']
    #                 #st.write(f"Recipe Text Preview: {text_preview}")
    #                 st.write(f"Recipe Text: {recipe['recipe_text']}")
    prompt = f"""
        
            Act as an expert {cuisine} chef. Generate **two creative and practical {cuisine} recipes** using only the specified ingredients.

            - First, check the list: if {query} includes any harmful, toxic, or inedible items, respond with:  
              "Sorry, one or more ingredients are not valid." Then stop.

            - If no ingredients are provided, reply:  
              "Please specify the ingredient(s). Don’t forget to press enter!" Then stop.

            - If ingredients are valid, continue and generate two unique recipes:
              - Use **only** the following:
                  - **Ingredients**: {ingredients}
                  - **Protein**: {protein} (optional – adjust or skip)
                  - **Carbs**: {carb} (optional – adjust or skip)
                  - **Cuisine**: {cuisine}
              - Ensure total **cooking time is under {time} minutes**
              - You may use **very small amounts of common flavor enhancers** (e.g., oil, salt, spices), but **do not add new main ingredients**
              - If cuisine is **Indian**, take inspiration from the provided Indian recipe, but **do not copy it**

            For **each recipe**, output:
            - A compelling and descriptive recipe name
            - A short summary (flavor profile, uniqueness)
            - Ingredient list (only from the allowed items)
            - Clear, step-by-step cooking instructions
            - Prep time, cook time, and total time
            - Estimated calories with a short note on how they were calculated
            - Emphasize flavor, texture, ease, and uniqueness

            Avoid repetition—ensure both recipes are distinct from each other and from the example.

            ### Example Output Format:

            ### 🥘 Aloo Broccoli Paneer Tikki

            **Summary:**  
            A crispy, golden-brown patty made from mashed potato, crumbled paneer, and steamed broccoli, offering a satisfying blend of textures and flavors with {cuisine} spices.
                
            **Ingredients:**  
            - 1 cup broccoli, finely chopped  
            - 1 medium potato (boiled and mashed)  
            - 1 cup paneer, crumbled  
            - 1 tsp cumin powder  
            - ½ tsp coriander powder  
            - ½ tsp red chili powder  
            - 1 tbsp chopped cilantro  
            - Salt to taste  
            - 1–2 tbsp breadcrumbs (optional)  
            - 1 tbsp oil (for frying)
                
            **Instructions:**
            1. **Prep the filling (5 mins):** Boil and mash the potato. Steam and chop broccoli. Crumble the paneer.
            2. **Mix ingredients (5 mins):** Combine potato, paneer, broccoli, spices, and salt. Add breadcrumbs if needed for binding.
            3. **Shape the tikkis (5 mins):** Form small round or oval patties.
            4. **Fry (5–7 mins):** Heat oil and fry tikkis until golden and crispy, about 2–3 minutes per side.
            5. **Serve:** Enjoy with chutney or sauce.
                
            **Estimated Time Breakdown:**
            - Prep time: 5 mins
            - Cooking time: 10–12 mins
            - Frying time: 5–7 mins
            - Shaping time: 5 mins
                
            ✅ **Total Time:** ~15–17 minutes  
            🔥 **Calories (per serving):** ~180–220


            Five similar recipes for inspiration only if cuisine specified is Indian:
            {recipe_info}
            """



       
           
    chat_client = AzureOpenAIChat()
    response = chat_client.generate_response(prompt)
           #st.write(response)

    try:
        recipe_content = response["choices"][0]["message"]["content"]
        st.write(recipe_content)
        recipe_content = recipe_content.replace("```json", "").replace("```", "").strip()
    except (KeyError, IndexError, TypeError):
        st.error("Oops! Something went wrong while generating the recipes. Please try again.")
else:
        print("No similar recipes found.")

               
# container = st.container(border=True)
# with container:
#     st.markdown("<h4 style='text-align: center;'> Cool recipe ideas </h4>", unsafe_allow_html=True)
#     cols = container.columns(2)  # Split into two columns
    
#     card_data = [
#         {"title": "Card 1", "text": "This is some text for card 1.", "key": "btn1"},
#         {"title": "Card 2", "text": "This is some text for card 2.", "key": "btn2"}
#     ]
   
#     cols = st.columns(2)
    
#     for idx, col in enumerate(cols):
#         with col:
#             # Create a card with a border, image, and button
#             st.markdown("""
#             <div style="border: 2px solid #ddd; padding: 20px; text-align: center; border-radius: 10px;">
#             <img src="https://www.honeywhatscooking.com/wp-content/uploads/2023/11/Matar-Paneer-Recipe.jpg" alt="card image" style="border-radius: 10px;">
#             <h4>Card </h4>
#             <p> this is recipe idea  </p>
#             <button style="padding: 5px; background-color: white; color: red; border: none; border-radius: 5px;">Click Me</button>
#             </div>
#             """.format(idx + 1), unsafe_allow_html=True)
#     st.markdown("<div style=padding: 30px;>", unsafe_allow_html=True)
    
