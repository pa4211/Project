import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar
from search import RecipeEmbeddingSearch  # Importing the class from search.py
from search import AzureOpenAIChat
st.markdown('<h1 style="color: #FF5A5F;"> 😋 Meal Genie</h1>', unsafe_allow_html=True)




container = st.container(border=True)
with container:
    keywords = st_tags(
    label='Available Ingredients:',
        text='Press enter to add more',
        #value=["Carrots", "Onion"],
        #suggestions=['five', 'six', 'seven', 'eight', 'nine', 'three', 'eleven', 'ten', 'four'],
        maxtags=18,
        key="aljnf")
    ingredients = list(keywords)
    ingredients_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
    for ingredient in ingredients:
        ingredients_html += f'<div style="background-color: #F0F2F6; padding: 5px 10px; border-radius: 15px;">{ingredient}</div>'

    container.markdown(ingredients_html, unsafe_allow_html=True)


# col1, col2, col3 = st.columns(3,gap="small", border=True)

# color1 = col1.select_slider(
#     "Protein",
#     options=[
#         "Low",
#         "Medium",
#         "High",
        
#     ]
# )
# color2 = col2.select_slider(
#     "Carbs",
#     options=[
#          "Low",
#         "Medium",
#         "High",
#     ]
# )
# color3 = col3.select_slider(
#     "Fat",
#     options=[
#         "Low",
#         "Medium",
#         "High",
#     ]
# )

# left, right = st.columns(2,vertical_alignment="center", gap="small", border=True)
# options = ["10-15 mins", "15-30 mins", "30+ mins"]
# selection = left.pills("Cooking Time", options, selection_mode="single")


# options = ["<500 KCal", "<1000 KCal", "No Limits"]
# selection = right.pills("Calories", options, selection_mode="single")


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
           prompt =  f"""Act as a expert Indian chef. Your task is to generate two delicious, and practical Indian recipes that use all the ingredients specified.
First Check if one or more of the items in this ingredient list: {query} ,  are harmful or non-edible for humans to consume, then say "sorry"
Else Use the {ingredients} to come up with 2 recipe suggestions. Dont add new ingredients. 
Use only whats provided. Dont add new main ingredients. You are free to add other non-harmful ingredients that add flavor and taste, and that are available commonly at Indianhome.

Use the following five chef-created Indian recipes (listed separately below) as inspiration, but do not copy them. Instead, think creatively and come up with entirely new Indian recipes that blend traditional flavor, uniqueness, and everyday feasibility.

Only display recipes and no opening and closing lines. The recipe should be a meal recipe or dessert depending on ingredients input by
Each recipe you create should include:
A creative and descriptive recipe name
A brief summary of the dish (its flavor profile, what makes it unique)
A clear ingredient list (using only the provided ingredients)
Step-by-step cooking instructions that are easy to follow
 - Give time of prep, calories. Also tell how you arrived at the time and calories level.
- Do not add any additional ingredients beyond what's listed.

Guidelines:
- Focus on Indian flavor balance, texture, and innovation
- Dont add new ingredients
- Recipes should not be overly similar to the five provided examples
- Keep practicality and taste in mind!
- try not to increase the number of ingredients else it will become difficult for the user to get them

Example outpur 
**Example Output:**

###Recipe Name: 🥘 Aloo Broccoli Paneer Tikki

**Summary:**  
This is a crispy, golden-brown potato patty filled with crumbled paneer and steamed broccoli. It's a perfect snack or appetizer, offering a great blend of textures and flavors with simple Indian spices.

**Ingredients:**  
- 1 cup broccoli, finely chopped  
- 1 medium potato (aloo), boiled and mashed  
- 1 cup paneer, crumbled  
- 1 tsp cumin powder  
- ½ tsp coriander powder  
- ½ tsp red chili powder  
- 1 tbsp chopped cilantro  
- Salt to taste  
- 1–2 tbsp breadcrumbs (optional, for binding)  
- 1 tbsp oil (for frying)

**Instructions:**
1. **Prep the filling (5 mins):** Boil and mash the potato. Steam the broccoli for 2–3 minutes and chop it finely. Crumble the paneer.
2. **Mix ingredients (5 mins):** In a large bowl, combine mashed potato, crumbled paneer, chopped broccoli, cumin powder, coriander powder, red chili powder, and salt. Add chopped cilantro. If the mixture is too soft, add breadcrumbs for better binding.
3. **Shape the tikkis (5 mins):** Take small portions of the mixture and shape them into round or oval patties.
4. **Fry (5–7 mins):** Heat oil in a non-stick pan. Fry the tikkis on medium heat for 2–3 minutes per side, or until golden and crisp.
5. **Serve:** Serve hot with mint chutney or tamarind sauce.

**Estimated Time Breakdown:**
- Prep time: 5 mins
- Cooking time: 10–12 mins
- Frying time: 5–7 mins
- Shaping time: 5 mins

✅ **Total Time:** ~15–17 minutes  
🔥 **Calories (per serving):** ~180–220  
(Main calorie contributors: potato and paneer; broccoli adds fiber and nutrients.)
\n\n{recipe_info}\n\n

Dont add any opening or closing lines. Just give recipes
"""
           
           
           chat_client = AzureOpenAIChat()
           response = chat_client.generate_response(prompt)
        
           recipe_content = response["choices"][0]["message"]["content"]
           recipe_content = recipe_content.replace("```json", "").replace("```", "").strip()
           st.write(recipe_content)
    # else:
    #             print("No similar recipes found.")

               
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
    
