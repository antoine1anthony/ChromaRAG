# ChromaRAG Document Upload UI

A Next.js-based web interface for uploading documents to the ChromaRAG API with collection management and metadata support.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ installed
- Yarn package manager
- ChromaRAG API server running on `http://localhost:8000`

### Installation & Running

1. **Start the development server:**
   ```bash
   cd testerdirectory/web
   yarn dev
   ```

2. **Access the application:**
   Open [http://localhost:3000](http://localhost:3000) in your browser

## 🎯 Features

### ✅ Collection Management
- **Create new collections** with custom names
- **Select existing collections** for document upload
- Automatic collection dropdown population

### ✅ Document Upload
- **Multiple document support** - add/remove document forms dynamically
- **File upload** - supports `.txt`, `.md`, `.json`, `.csv` files
- **Manual text input** - paste or type content directly
- **Metadata support** - JSON-formatted metadata for each document
- **URI support** - link to external document sources

### ✅ API Integration
- **Authentication** - automatic API key handling
- **Error handling** - clear error messages and validation
- **Success feedback** - confirmation of successful uploads
- **Background processing** - documents processed asynchronously

### ✅ User Experience
- **Responsive design** - works on desktop and mobile
- **Form validation** - ensures required fields are filled
- **Auto-population** - file uploads auto-fill document fields
- **JSON metadata editor** - with syntax validation

## 📋 How to Use

### Step 1: Collection Setup
1. **Create a new collection:**
   - Enter a collection name in the "Create New Collection" field
   - Click "Create" button
   - Collection will be created and selected automatically

2. **Or select existing collection:**
   - Choose from the dropdown in "Select Collection for Upload"

### Step 2: Document Upload
1. **Add documents:**
   - Click "+ Add Document" to add more document forms
   - Each document requires a unique ID

2. **Fill document data:**
   - **Document ID** (required): Unique identifier
   - **URI** (optional): External link to document
   - **File Upload**: Upload text files directly
   - **Text Content**: Manual text input or auto-filled from file
   - **Metadata**: JSON format for labels, categories, tags, etc.

3. **Example metadata:**
   ```json
   {
     "category": "research",
     "tags": ["ai", "ml", "nlp"],
     "author": "John Doe",
     "department": "Engineering",
     "priority": "high"
   }
   ```

### Step 3: Upload
1. Click "Upload Documents" button
2. Wait for success confirmation
3. Documents are processed in the background

## 🔧 API Configuration

The frontend connects to the ChromaRAG API with these settings:

- **API Base URL:** `http://localhost:8000`
- **API Key:** `your-secure-api-key` (configured in header)
- **CORS:** Enabled for `localhost:3000`

### API Endpoints Used:
- `POST /collections/create_collection` - Create collections
- `POST /documents/add_documents_background/{collection_name}` - Upload documents

## 🛠️ Technical Details

### Built With:
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React Hooks** for state management

### Key Components:
- **Collection Management** - Create and select collections
- **Document Forms** - Dynamic document input forms
- **File Handling** - File upload and text extraction
- **API Integration** - RESTful API communication
- **Error Handling** - User-friendly error messages

### File Structure:
```
testerdirectory/web/
├── app/
│   ├── page.tsx          # Main document upload interface
│   ├── layout.tsx        # App layout and metadata
│   └── globals.css       # Global styles
├── package.json          # Dependencies and scripts
└── tailwind.config.ts    # Tailwind CSS configuration
```

## 🔍 Supported File Types

- **Text files:** `.txt`
- **Markdown:** `.md`
- **JSON:** `.json`
- **CSV:** `.csv`

Files are automatically read and their content is populated in the text field.

## ⚠️ Important Notes

1. **API Server Required:** The ChromaRAG API server must be running on port 8000
2. **CORS Configuration:** Backend includes CORS support for localhost:3000
3. **API Key:** Uses hardcoded API key (`your-secure-api-key`) for development
4. **Background Processing:** Documents are processed asynchronously
5. **Unique IDs:** Each document must have a unique identifier

## 🚨 Troubleshooting

### Common Issues:

1. **"Network error: Could not connect to API"**
   - Ensure ChromaRAG API server is running on port 8000
   - Check that CORS is properly configured in the backend

2. **"Collection name is required"**
   - Enter a valid collection name before creating

3. **"Please provide at least one document with an ID and content"**
   - Ensure each document has both an ID and either text content or URI

4. **JSON Metadata Errors**
   - Check JSON syntax in metadata fields
   - Use proper quotes and brackets

### Checking Server Status:
```bash
# Check if servers are running
lsof -i :3000 -i :8000

# Should show:
# - node (port 3000) - Next.js frontend
# - Python (port 8000) - FastAPI backend
```

## 📝 Example Usage

1. Create collection: "research-papers"
2. Upload document:
   - ID: "paper-001"
   - Text: "This is a research paper about machine learning..."
   - Metadata: `{"category": "AI", "tags": ["ML", "research"]}`
3. Click "Upload Documents"
4. Success! Document is now in ChromaRAG

## 🔄 Development

To modify the interface:

1. Edit `app/page.tsx` for UI changes
2. Modify API calls for different endpoints
3. Update styling in Tailwind classes
4. Add new features using React hooks

Happy documenting! 🎉 