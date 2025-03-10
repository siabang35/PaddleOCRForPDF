import streamlit as st
import requests
import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any

# API configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Research Paper Vidavox Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .reportview-container {
        background: #f0f2f6;
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

class APIClient:
    """API client for interacting with the backend."""
    
    @staticmethod
    def load_document(doc_id: int) -> Optional[Dict[str, Any]]:
        """Load document data from API."""
        try:
            response = requests.get(f"{API_URL}/documents/{doc_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                st.error("Document not found!")
            else:
                st.error(f"Error loading document: {response.text}")
            return None
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")
            return None
    
    @staticmethod
    def search_documents(query: str) -> Optional[list]:
        """Search documents through API based on query."""
        try:
            response = requests.post(
                f"{API_URL}/search",
                json={"query": query, "limit": 10}  # Tidak ada min_rank
            )
            response.raise_for_status()  # Tangani HTTP error
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to API: {str(e)}")
            return None

class DocumentViewer:
    """Component for viewing document details."""
    
    @staticmethod
    def render_document(document: Dict[str, Any]):
        """Render document content and metadata."""
        # Document content
        st.subheader("📝 Content")
        st.text_area(
            "Document Text",
            document["content"],
            height=200,
            help="Full text content of the document"
        )
        
        # Named Entities
        st.subheader("🏷️ Named Entities")
        if document["entities"]:
            entities_df = pd.DataFrame(document["entities"])
            st.dataframe(entities_df)
        else:
            st.info("No named entities found")
        
        # Keywords
        st.subheader("🔑 Keywords")
        if document["keywords"]:
            st.write(" • ".join(document["keywords"]))
        else:
            st.info("No keywords extracted")
        
        # Charts
        if document["charts"]:
            st.subheader("📊 Charts")
            cols = st.columns(len(document["charts"]))
            for idx, (col, chart) in enumerate(zip(cols, document["charts"])):
                with col:
                    image_path = Path(chart["image_path"])
                    if image_path.exists():
                        image = Image.open(image_path)
                        st.image(
                            image,
                            caption=f"Chart {idx + 1}",

                        )
                        st.metric(
                            "Confidence Score",
                            f"{chart['confidence']:.2%}"
                        )
                        with st.expander("Chart Details"):
                            st.json(chart["characteristics"])
                    else:
                        st.error(f"Image not found: {image_path}")

class SearchInterface:
    """Component for document search interface."""

    @staticmethod
    def render_search_interface():
        """Render search interface and results."""
        st.subheader("🔍 Input Number for Search Documents")

        # Input query dalam satu kolom
        query = st.text_input(
            "Search Query",
            help="Enter keywords to search for in documents"
        )

        # Proses pencarian ketika query tidak kosong
        if query:
            results = APIClient.search_documents(query)  # Hapus min_rank
            if results and isinstance(results, list):
                st.subheader(f"📚 Found {len(results)} Results")

                for result in results:
                    with st.expander(f"📄 Document {result.get('id', 'Unknown')}"):
                        st.write(result.get("content", "No content available")[:300] + "...")
                        
                        # Keywords
                        keywords = result.get("keywords", [])
                        if keywords:
                            st.write("🏷️ Keywords:", " • ".join(keywords))
                        else:
                            st.info("No keywords found")

                        # Charts
                        charts = result.get("charts", [])
                        if charts:
                            st.write(f"📊 Contains {len(charts)} charts")
            else:
                st.info("No matching documents found")


def main():
    """Main application entry point."""
    st.title("📄 Research Paper Vidavox Analysis")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Document Viewer", "Search"])
    
    if page == "Document Viewer":
        st.header("📖 Document Viewer")
        doc_id = st.number_input(
            "Document ID",
            min_value=1,
            value=1,
            help="Enter the ID of the document to view"
        )
        
        if st.button("Load Document", key="load_doc"):
            document = APIClient.load_document(doc_id)
            if document:
                DocumentViewer.render_document(document)
    
    else:  # Search page
        SearchInterface.render_search_interface()

if __name__ == "__main__":
    main()