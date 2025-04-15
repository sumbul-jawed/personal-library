import streamlit as st
import pandas as pd 
import json 
import os 
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go 
from streamlit_lottie import st_lottie
import requests

# Set Page Configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Styling
st.markdown("""
<style>
/* Global styles */
body {
    background-color: #F9FAFB;
    color: #1F2937;
    font-family: 'Inter', sans-serif;
}

/* Main header */
.main-header {
    font-size: 2.5rem !important;
    color: #2563EB;
    font-weight: 700;
    margin-bottom: 1.5rem;
    text-align: center;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}

/* Subheader */
.sub_header {
    font-size: 1.5rem !important;
    color: #2563EB;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Success message */
.success-message {
    padding: 1rem;
    background-color: #ECFDF5;
    border-left: 5px solid #059669;
    border-radius: 8px;
    color: #1F2937;
    font-weight: 500;
}

/* Warning message */
.warning-message {
    padding: 1rem;
    background-color: #FFFBEB;
    border-left: 5px solid #D97706;
    border-radius: 8px;
    color: #1F2937;
    font-weight: 500;
}

/* Book card */
.book-card {
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    border-left: 5px solid #2563EB;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    transition: transform 0.2s ease;
}
.book-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

/* Badges */
.read-badge {
    background-color: #059669;
    color: #FFFFFF;
    padding: 0.3rem 0.8rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
}
.unread-badge {
    background-color: #EF4444;
    color: #FFFFFF;
    padding: 0.3rem 0.8rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    background-color: #2563EB;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: background-color 0.2s;
}
.stButton > button:hover {
    background-color: #1D4ED8;
}

/* Sidebar */
.sidebar .sidebar-content {
    background-color: #FFFFFF;
    border-right: 1px solid #E5E7EB;
}
.sidebar h1 {
    color: #2563EB;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
}
.stRadio > label {
    color: #1F2937;
    font-size: 1rem;
    font-weight: 500;
}
.stRadio > div > label > div {
    border: 2px solid #2563EB;
}

/* Footer */
.footer {
    position: relative;
    bottom: 0;
    width: 100%;
    text-align: center;
    color: #6B7280;
    padding: 1.5rem 0;
    font-size: 0.9rem;
    border-top: 1px solid #E5E7EB;
}

/* Responsive design */
@media (max-width: 640px) {
    .main-header {
        font-size: 2rem !important;
    }
    .sub_header {
        font-size: 1.25rem !important;
    }
    .book-card {
        padding: 1rem;
    }
    .stButton > button {
        padding: 0.4rem 0.8rem;
        font-size: 0.9rem;
    }
    .sidebar .sidebar-content {
        padding: 1rem;
    }
}

/* Plotly charts */
.plotly-chart {
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# Load lottie
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Session states
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load Library
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error Loading library: {e}")
        return False 

# Save library
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error Saving library: {e}")
        return False 

# Add book
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Library status
def get_library_status():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}  
    authors = {}  
    decades = {}

    for book in st.session_state.library:
        # Genre count
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        # Author count
        authors[book['author']] = authors.get(book['author'], 0) + 1
        # Decade count
        publication_year = book.get('publication_year', None)
        if publication_year is not None and isinstance(publication_year, (int, float)):
            decade = (int(publication_year) // 10) * 10
            decades[decade] = decades.get(decade, 0) + 1

    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Visualizations
def create_visualizations(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=.4,
            marker_colors=['#059669', '#EF4444']
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values()),
        })
        fig_genres = px.bar(
            genres_df,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genre',
            yaxis_title='Number of Books',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#2563EB']
        )
        fig_decades.update_layout(
            title_text='Books by Publication Decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# Load the library
load_library()

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_aKAfIn.json")
if lottie_book:
    st_lottie(lottie_book, height=200, key='book_animation')

nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"],
    key="nav_radio"
)
if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"

st.markdown("<h1 class='main-header'>Personal Library Manager 📖</h1>", unsafe_allow_html=True)

# --- Add Book View ---
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("📖 Book Title", max_chars=100)
        author = st.text_input("✍️ Author", max_chars=100)
        publication_year = st.number_input("📅 Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2024)

    with col2:
        genre = st.selectbox("Genre", [
            "Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "Romance", 
            "Poetry", "Self-help", "Art", "Religion", "History", "Programming", "Productivity", "Machine Learning", "Others"
        ])
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
        read_book = read_status == "Read"

    with st.form("add_book_form"):
        submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_book)
            if st.session_state.book_added:
                st.markdown("<div class='success-message'>✅ Book added Successfully!</div>", unsafe_allow_html=True)
                st.balloons()
                st.session_state.book_added = False

# --- Library View ---
elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub_header'>📚 Your Library</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""<div class='book-card'>
                <h3>{book['title']}</h3>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Publication Year:</strong> {book.get('publication_year', 'N/A')}</p>
                <p><strong>Genre:</strong> {book['genre']}</p>
                <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{
                    "Read" if book["read_status"] else "Unread"
                }</span></p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                            st.session_state.book_removed = True

                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()

    if st.session_state.book_removed:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False

# --- Search View ---
elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)

    search_by = st.selectbox("🔍 Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter Search Term:")

    if st.button("Search", use_container_width=False):
        with st.spinner("Searching..."):
            time.sleep(0.5)
            search_books(search_term, search_by)

        if st.session_state.search_results:
            st.markdown(f"<h3>📖 Found {len(st.session_state.search_results)} Result(s):</h3>", unsafe_allow_html=True)
            for i, book in enumerate(st.session_state.search_results):
                st.markdown(f"""<div class='book-card'>
                <h3>{book['title']}</h3>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Publication Year:</strong> {book.get('publication_year', 'N/A')}</p>
                <p><strong>Genre:</strong> {book['genre']}</p>
                <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{
                    "Read 📘" if book["read_status"] else "Unread 📕"
                }</span></p>
                </div>
                """, unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>⚠️ No books found matching your search.</div>", unsafe_allow_html=True)

# --- Stats View ---
elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>📊 Library Statistics</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>⚠️ Your library is empty. Add some books to see stats!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_status()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books 📚", stats['total_books'])
        with col2:
            st.metric("Books Read ✅", stats['read_books'])
        with col3:
            st.metric("Read Percentage 📈", f"{stats['percent_read']:.1f}%")

        create_visualizations(stats)

        if stats['authors']:
            st.markdown("<h3>👩‍💻 Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")

st.markdown("---")
st.markdown("<div class='footer'>📚 Made with ❤️ by Sumbul Jawed — Personal Library Manager</div>", unsafe_allow_html=True)
