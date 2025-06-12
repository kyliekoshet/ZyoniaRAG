import pytest
from pathlib import Path
import pandas as pd
import os
from airz.loaders import load_any, split_docs

@pytest.fixture
def test_dir(tmp_path):
    """Create test files of different types."""
    # Create a test directory
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    
    # Create a text file
    text_file = test_dir / "sample.txt"
    text_file.write_text("This is a test document.\nIt has multiple lines.")
    
    # Create a CSV file
    csv_file = test_dir / "sample.csv"
    df = pd.DataFrame({
        'col1': ['data1', 'data2'],
        'col2': ['info1', 'info2']
    })
    df.to_csv(csv_file, index=False)
    
    # Create an Excel file
    excel_file = test_dir / "sample.xlsx"
    df.to_excel(excel_file, index=False)
    
    # Create a PDF file (simple text-based)
    pdf_file = test_dir / "sample.pdf"
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(pdf_file))
    c.drawString(100, 750, "This is a test PDF document.")
    c.save()
    
    return test_dir

def test_load_text(test_dir):
    """Test loading a text file."""
    docs = load_any(test_dir / "sample.txt")
    assert len(docs) == 1
    assert "test document" in docs[0].page_content

def test_load_csv(test_dir):
    """Test loading a CSV file."""
    docs = load_any(test_dir / "sample.csv")
    assert len(docs) == 2  # Two rows in the CSV
    assert "data1" in docs[0].page_content

def test_load_excel(test_dir):
    """Test loading an Excel file."""
    docs = load_any(test_dir / "sample.xlsx")
    assert len(docs) > 0
    assert any("data" in doc.page_content for doc in docs)

def test_load_pdf(test_dir):
    """Test loading a PDF file."""
    docs = load_any(test_dir / "sample.pdf")
    assert len(docs) > 0
    assert "test PDF document" in docs[0].page_content

def test_load_directory(test_dir):
    """Test loading an entire directory."""
    docs = load_any(test_dir)
    # Should load all files (txt, csv, xlsx, pdf)
    assert len(docs) > 3

def test_split_docs(test_dir):
    """Test document splitting functionality."""
    # Create a long document
    long_text = "This is " + "very " * 100 + "long text"
    long_file = test_dir / "long.txt"
    long_file.write_text(long_text)
    
    docs = load_any(long_file)
    split = split_docs(docs, chunk_size=100, overlap=20)
    
    assert len(split) > 1  # Should be split into multiple chunks
    # Check overlap
    assert split[0].page_content[-20:] in split[1].page_content

def test_invalid_file():
    """Test handling of non-existent file."""
    with pytest.raises(Exception):
        load_any("nonexistent.txt") 