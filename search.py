import pinecone
from pinecone import Pinecone
from openai import AzureOpenAI
from typing import List, Dict, Any
import streamlit as st
import requests
import json

class AzureOpenAIChat:
    def __init__(self):
        self.API_ENDPOINT = st.secrets.get("AZURE_OPENAI_API_ENDPOINT", "")
        self.API_KEY = st.secrets.get("AZURE_OPENAI_API_KEY", "")

    def generate_response(self, query: str)->Dict[str, Any]:
    #def generate_response(self, query: str, max_tokens: int = 2000)->Dict[str, Any]:
        """Generate response from Azure OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.API_KEY,
        }

        data = {
            "messages": [{"role": "user", "content": query}],
            #"max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        
        }
        try:
            response = requests.post(self.API_ENDPOINT, headers=headers, json=data)
            response.raise_for_status()  # Automatically raises an error for HTTP issues
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error: API request failed.", str(e))
        return {} 
class RecipeEmbeddingSearch:
    def __init__(self, 
                 index_name="recipe-embeddings", 
                 azure_endpoint="https://access-01.openai.azure.com",
                 pinecone_api_key="PINECONE_API_KEY",#
                 api_key="your_azure_api_key",
                 deployment_name="text-embedding-3-large",
                 api_version="2023-05-15"):
        """
        Initialize Pinecone connection and Azure OpenAI client using the new SDK
        """
        # Configure Azure OpenAI client with new SDK
        self.API_KEY = st.secrets.get("PINECORE_API_KEY", "")
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        self.deployment_name = deployment_name
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Connect to the existing Pinecone index
        self.index = self.pc.Index(index_name)
        
        # Get index details to check dimensions
        try:
            index_stats = self.index.describe_index_stats()
            print(f"Connected to Pinecone index: {index_name}")
            self.dimension = index_stats.dimension  # Get actual index dimension
            print(f"Index dimension: {self.dimension}")
            print(f"Total vectors: {index_stats.total_vector_count}")
        except Exception as e:
            print(f"Warning: Could not get index stats: {e}")
            self.dimension = 3072  # Default to 3072 for text-embedding-3-large
    def generate_query_embedding(self, query_text: str) -> List[float]:
            """
            Generate embedding for the search query using Azure OpenAI
            """
            try:
                # Create embedding using new Azure OpenAI SDK syntax
                response = self.client.embeddings.create(
                    input=query_text,
                    model=self.deployment_name
                )
                
                # Extract the embedding - new SDK structure
                embedding = response.data[0].embedding
                
                print(f"Generated embedding dimension: {len(embedding)}")
                return embedding
            except Exception as e:
                print(f"Error generating embedding: {e}")
                # Return zero vector with correct dimension
                return [0.0] * self.dimension
    def search_similar_recipes(
        self, 
        query_text: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar recipes based on query text
        """
        try:
            # Generate embedding for the query
            query_embedding = self.generate_query_embedding(query_text)
            
            # Search in Pinecone index
            results = self.index.query(
                vector=query_embedding, 
                top_k=top_k,
                include_metadata=True
            )
            
            # Updated structure for new Pinecone SDK
            similar_recipes = []
            for match in results.matches:
                recipe = {
                    'id': match.id,
                    'score': match.score,
                    'recipe_name': match.metadata.get('recipe_name', 'Unknown Recipe'),
                    'recipe_text': match.metadata.get('recipe_text', 'No recipe details')
                }
                similar_recipes.append(recipe)
            
            return similar_recipes
        
        except Exception as e:
            print(f"Error in recipe search: {e}")
            print(f"Full error details: {str(e)}")
            return []        
def main():
        # Initialize the recipe search
        recipe_search = RecipeEmbeddingSearch(
              index_name="recipe-embeddings",

            azure_endpoint="https://access-01.openai.azure.com",



            
            pinecone_api_key=st.secrets["pinecone"]["api_key"],

            deployment_name="text-embedding-3-large",
            
            api_key = st.secrets["whisper"]["api_key"],
            api_version="2023-05-15"
        )
        
        search_queries = [
        "onion",
         ]
    
    # Perform searches
        for query in search_queries:
           
            similar_recipes = recipe_search.search_similar_recipes(query)
             # Print results
            if similar_recipes:
                for i, recipe in enumerate(similar_recipes, 1):
                    st.write(f"\nResult {i}:")
                    st.write(f"Recipe Name: {recipe['recipe_name']}")
                    st.write(f"Similarity Score: {recipe['score']:.4f}")
                    #text_preview = recipe['recipe_text'][:500] + "..." if len(recipe['recipe_text']) > 500 else recipe['recipe_text']
                    #st.write(f"Recipe Text Preview: {text_preview}")
                    st.write(f"Recipe Text: {recipe['recipe_text']}")
            else:
                print("No similar recipes found.")
               

        

if __name__ == "__main__":
    main()