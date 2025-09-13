import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="AI Travel Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

class StreamlitTravelApp:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        """Initialize session state variables"""
        if 'current_recommendations' not in st.session_state:
            st.session_state.current_recommendations = []
        if 'liked_properties' not in st.session_state:
            st.session_state.liked_properties = []
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {}
        if 'current_swipe_index' not in st.session_state:
            st.session_state.current_swipe_index = 0

    def make_api_request(self, endpoint, data=None):
        """Make API request to Flask backend"""
        try:
            if data:
                response = requests.post(f"{API_BASE_URL}{endpoint}", json=data)
            else:
                response = requests.get(f"{API_BASE_URL}{endpoint}")
            return response.json()
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to backend. Please make sure the Flask server is running on port 5000.")
            return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def render_header(self):
        """Render the main header"""
        st.title("🌍 AI Travel Platform")
        st.markdown("*Discover your perfect trip with AI-powered recommendations*")

        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Search", "🤖 AI Agent", "❤️ Swipe & Match", "🛡️ Safety", "👥 Social"
        ])

        return tab1, tab2, tab3, tab4, tab5

    def render_search_tab(self, tab):
        """Render the search functionality"""
        with tab:
            st.header("🔍 Search Properties")

            col1, col2 = st.columns(2)

            with col1:
                city = st.text_input("🏙️ City", placeholder="e.g., San Francisco")
                room_type = st.selectbox("🏠 Room Type",
                    ["Any", "Entire home/apt", "Private room", "Shared room"])
                min_price = st.number_input("💰 Min Price ($)", min_value=0, value=0)

            with col2:
                max_price = st.number_input("💰 Max Price ($)", min_value=0, value=1000)
                min_rating = st.slider("⭐ Minimum Rating", 0.0, 5.0, 3.0, 0.1)
                activities = st.multiselect("🎯 Activities",
                    ["whales", "beaches", "mountains", "culture", "food", "nightlife", "adventure"])

            if st.button("🔍 Search Properties", type="primary"):
                filters = {
                    "city": city if city else None,
                    "room_type": room_type if room_type != "Any" else None,
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_rating": min_rating,
                    "activities": activities
                }

                result = self.make_api_request("/search", filters)
                if result and result.get('success'):
                    self.display_search_results(result['properties'])
                else:
                    st.error("Search failed. Please try again.")

    def render_ai_agent_tab(self, tab):
        """Render the AI agent functionality"""
        with tab:
            st.header("🤖 AI Travel Agent")
            st.markdown("Tell me what you want to do, and I'll find the perfect places for you!")

            # Example queries
            st.markdown("**Try these examples:**")
            examples = [
                "I want to see whales in California",
                "Find me a mountain cabin for skiing",
                "Beach house for a family vacation",
                "Cultural experience in a historic city"
            ]

            example_cols = st.columns(2)
            for i, example in enumerate(examples):
                with example_cols[i % 2]:
                    if st.button(f"💡 {example}", key=f"example_{i}"):
                        st.session_state.ai_query = example

            # Query input
            query = st.text_area("🗣️ What kind of trip are you looking for?",
                               value=st.session_state.get('ai_query', ''),
                               placeholder="e.g., I want to see whales and enjoy local seafood in a coastal town")

            if st.button("🚀 Get AI Recommendations", type="primary"):
                if query:
                    result = self.make_api_request("/ai-agent", {"query": query})
                    if result and result.get('success'):
                        self.display_ai_results(result)
                    else:
                        st.error("AI query failed. Please try again.")
                else:
                    st.warning("Please enter a travel query.")

    def render_swipe_tab(self, tab):
        """Render the swipe-based matching functionality"""
        with tab:
            st.header("❤️ Swipe & Match Your Perfect Trip")

            # Get recommendations if not already loaded
            if not st.session_state.current_recommendations:
                if st.button("🎯 Get Personalized Recommendations"):
                    preferences = {
                        "activities": ["beaches", "culture", "food"],
                        "budget": 300
                    }
                    result = self.make_api_request("/recommendations", {"preferences": preferences})
                    if result and result.get('success'):
                        st.session_state.current_recommendations = result['recommendations']
                        st.session_state.current_swipe_index = 0
                        st.rerun()

            # Display swipe interface
            if st.session_state.current_recommendations:
                self.render_swipe_interface()
            else:
                st.info("Click 'Get Personalized Recommendations' to start swiping!")

    def render_swipe_interface(self):
        """Render the swipe interface"""
        recommendations = st.session_state.current_recommendations
        current_index = st.session_state.current_swipe_index

        if current_index >= len(recommendations):
            st.success("🎉 You've seen all recommendations! Here are your liked properties:")
            self.display_liked_properties()
            return

        current_property = recommendations[current_index]

        # Display current property
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(f"### {current_property['name']}")
            st.markdown(f"📍 **{current_property['city']}, {current_property['country']}**")
            st.markdown(f"💰 **${current_property['price']}/night**")
            st.markdown(f"⭐ **{current_property['rating']} ({current_property['reviews']} reviews)**")
            st.markdown(f"🏠 **{current_property['room_type']}** • {current_property['accommodates']} guests")

            # Amenities
            amenities_str = " • ".join(current_property['amenities'])
            st.markdown(f"🎯 **Amenities:** {amenities_str}")

            # Activities
            activities_str = " • ".join(current_property['activities'])
            st.markdown(f"🏃 **Activities:** {activities_str}")

        # Swipe buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("👎 Pass", type="secondary", use_container_width=True):
                st.session_state.current_swipe_index += 1
                st.rerun()

        with col3:
            if st.button("❤️ Like", type="primary", use_container_width=True):
                st.session_state.liked_properties.append(current_property)
                st.session_state.current_swipe_index += 1
                st.success("Added to your favorites!")
                st.rerun()

        # Progress
        progress = (current_index + 1) / len(recommendations)
        st.progress(progress)
        st.markdown(f"Property {current_index + 1} of {len(recommendations)}")

    def render_safety_tab(self, tab):
        """Render safety information"""
        with tab:
            st.header("🛡️ Safety Information")

            location = st.text_input("🌍 Enter Location", placeholder="e.g., San Francisco, CA")

            if st.button("🔍 Get Safety Info", type="primary"):
                if location:
                    result = self.make_api_request("/safety", {"location": location})
                    if result and result.get('success'):
                        self.display_safety_info(result['safety_info'])
                    else:
                        st.error("Could not retrieve safety information.")
                else:
                    st.warning("Please enter a location.")

    def render_social_tab(self, tab):
        """Render social features"""
        with tab:
            st.header("👥 Connect with Fellow Travelers")

            st.markdown("### Find Travel Companions")

            col1, col2 = st.columns(2)

            with col1:
                travel_style = st.selectbox("🎒 Travel Style",
                    ["Adventure", "Cultural", "Relaxation", "Party", "Family"])
                interests = st.multiselect("🎯 Interests",
                    ["Hiking", "Photography", "Food", "Nightlife", "Museums", "Sports"])

            with col2:
                age_range = st.slider("👥 Age Range", 18, 70, (25, 35))
                destination = st.text_input("📍 Destination", placeholder="Where are you traveling?")

            if st.button("🔍 Find Travel Companions", type="primary"):
                profile = {
                    "travel_style": travel_style.lower(),
                    "interests": [interest.lower() for interest in interests],
                    "age_range": age_range,
                    "destination": destination
                }

                result = self.make_api_request("/social/connect", {"profile": profile})
                if result and result.get('success'):
                    self.display_travel_matches(result['matches'])
                else:
                    st.error("Could not find travel companions.")

    def display_search_results(self, properties):
        """Display search results"""
        st.markdown(f"### Found {len(properties)} properties")

        for prop in properties:
            with st.expander(f"{prop['name']} - ${prop['price']}/night"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"📍 **Location:** {prop['city']}, {prop['country']}")
                    st.markdown(f"🏠 **Type:** {prop['room_type']}")
                    st.markdown(f"👥 **Accommodates:** {prop['accommodates']} guests")
                    st.markdown(f"⭐ **Rating:** {prop['rating']} ({prop['reviews']} reviews)")

                with col2:
                    st.markdown(f"🛏️ **Bedrooms:** {prop['bedrooms']}")
                    st.markdown(f"🚿 **Bathrooms:** {prop['bathrooms']}")
                    st.markdown(f"🛡️ **Safety Score:** {prop['safety_score']}/5")

                    amenities_str = ", ".join(prop['amenities'])
                    st.markdown(f"🎯 **Amenities:** {amenities_str}")

                if st.button(f"📅 Book Now", key=f"book_{prop['id']}"):
                    st.success("Booking feature coming soon!")

    def display_ai_results(self, result):
        """Display AI agent results"""
        st.markdown("### 🤖 AI Analysis")

        intent = result.get('intent', {})
        if intent:
            st.markdown("**Understood your request:**")
            if intent.get('activities'):
                st.markdown(f"🎯 **Activities:** {', '.join(intent['activities'])}")
            if intent.get('location'):
                st.markdown(f"📍 **Location:** {intent['location']}")

        recommendations = result.get('recommendations', [])
        if recommendations:
            st.markdown(f"### 🏆 Top {len(recommendations)} Recommendations")
            self.display_search_results(recommendations)

    def display_safety_info(self, safety_info):
        """Display safety information"""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🛡️ Overall Safety")

            safety_level = safety_info['overall_safety']
            if safety_level == 'Low Risk':
                st.success(f"✅ {safety_level}")
            elif safety_level == 'Moderate Risk':
                st.warning(f"⚠️ {safety_level}")
            else:
                st.error(f"🚨 {safety_level}")

            st.markdown(f"**Crime Rate:** {safety_info['crime_rate']}/5")
            st.markdown(f"**Health Advisory:** {safety_info['health_advisory']}")

        with col2:
            st.markdown("### 📞 Emergency Contacts")
            contacts = safety_info['emergency_contacts']
            for service, number in contacts.items():
                st.markdown(f"**{service.title()}:** {number}")

        st.markdown("### 📰 Current Events")
        for event in safety_info['current_events']:
            st.markdown(f"• {event}")

    def display_travel_matches(self, matches):
        """Display travel companion matches"""
        st.markdown("### 🎯 Potential Travel Companions")

        for match in matches:
            with st.expander(f"{match['name']} - {match['travel_style'].title()} Traveler"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"👤 **Age:** {match['age']}")
                    st.markdown(f"🎒 **Travel Style:** {match['travel_style'].title()}")
                    st.markdown(f"✅ **Safety Verified:** {'Yes' if match['safety_verified'] else 'No'}")

                with col2:
                    interests_str = ", ".join(match['interests'])
                    st.markdown(f"🎯 **Interests:** {interests_str}")
                    st.markdown(f"🤝 **Mutual Connections:** {match['mutual_connections']}")

                if st.button(f"💬 Connect with {match['name']}", key=f"connect_{match['user_id']}"):
                    st.success("Connection request sent!")

    def display_liked_properties(self):
        """Display liked properties from swipe session"""
        if st.session_state.liked_properties:
            st.markdown("### ❤️ Your Liked Properties")
            for prop in st.session_state.liked_properties:
                with st.expander(f"{prop['name']} - ${prop['price']}/night"):
                    st.markdown(f"📍 {prop['city']}, {prop['country']}")
                    st.markdown(f"⭐ {prop['rating']} rating")
                    if st.button(f"📅 Book {prop['name']}", key=f"book_liked_{prop['id']}"):
                        st.success("Booking feature coming soon!")
        else:
            st.info("No liked properties yet. Start swiping to find your favorites!")

    def render_sidebar(self):
        """Render sidebar with additional features"""
        with st.sidebar:
            st.markdown("## 🌍 Travel Tools")

            # Language selector
            st.markdown("### 🌐 Language")
            language = st.selectbox("Select Language",
                ["English", "Spanish", "French", "German", "Italian", "Portuguese"])

            # Quick stats
            st.markdown("### 📊 Your Activity")
            st.metric("Properties Viewed", len(st.session_state.get('viewed_properties', [])))
            st.metric("Favorites", len(st.session_state.liked_properties))

            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            if st.button("🔄 Reset Preferences"):
                st.session_state.user_preferences = {}
                st.session_state.liked_properties = []
                st.session_state.current_swipe_index = 0
                st.success("Preferences reset!")

            if st.button("📱 Share Trip"):
                st.info("Social sharing coming soon!")

    def run(self):
        """Main application runner"""
        self.render_sidebar()
        tab1, tab2, tab3, tab4, tab5 = self.render_header()

        self.render_search_tab(tab1)
        self.render_ai_agent_tab(tab2)
        self.render_swipe_tab(tab3)
        self.render_safety_tab(tab4)
        self.render_social_tab(tab5)

# Run the app
if __name__ == "__main__":
    app = StreamlitTravelApp()
    app.run()
