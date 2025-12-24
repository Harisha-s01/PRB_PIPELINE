from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
import re

class ExtractiveAnswerGenerator:
    """Deterministic extractive answer generator from retrieved documents"""

    def __init__(self):
        # Regex patterns for factual extraction
        self.date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
            r'\b\d{4}-\d{2}\b',  # YYYY-MM (academic years like 2023-24)
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\bDate:\s*([^\n\r]+)',  # Date: something
        ]
        self.id_patterns = [
            r'\b[A-Z]{2,}-\d{4,}\b',  # Like PBR-20251224
            r'\b[A-Z]{3,}\d{4,}\b',   # Like PBR20251224
            r'\b\d{4,}[A-Z]{2,}\b',   # Like 2025PBR
            r'\bID:\s*[\w-]+\b',
            r'\bCode:\s*[\w-]+\b',
            r'\bBaseline\s+ID:\s*([^\n\r]+)',
            r'\bPBR:\s*([^\n\r]+)',
        ]
        self.number_patterns = [
            r'\b\d+(?:\.\d+)?\b'  # Numbers with optional decimals
        ]

    def generate_answer(self, question, retrieved_chunks):
        """Generate answer from retrieved document chunks"""
        if not retrieved_chunks:
            return "The requested information is not available in the provided documents."

        # Extract text from chunks
        chunk_texts = [chunk.page_content for chunk in retrieved_chunks]
        full_text = ' '.join(chunk_texts)

        # Try to extract factual information
        factual_answer = self._extract_factual_answer(question, full_text)
        if factual_answer:
            return factual_answer

        # No factual information found
        return "The requested information is not available in the provided documents."

    def _extract_factual_answer(self, question, text):
        """Extract factual information based on question type"""
        question_lower = question.lower()

        # Date questions
        if any(word in question_lower for word in ['date', 'when', 'day', 'month', 'year']):
            dates = self._extract_dates(text)
            if dates:
                if len(dates) == 1:
                    return f"The date is {dates[0]}."
                else:
                    return f"The dates mentioned are: {', '.join(dates)}."

        # ID/Code/Baseline questions
        if any(word in question_lower for word in ['id', 'code', 'number', 'baseline', 'pbr']):
            ids = self._extract_ids(text)
            if ids:
                if len(ids) == 1:
                    return f"The ID is {ids[0]}."
                else:
                    return f"The IDs mentioned are: {', '.join(ids)}."

        # Name/Title/Product questions
        if any(word in question_lower for word in ['name', 'title', 'product', 'called']):
            names = self._extract_names(question, text)
            if names:
                if len(names) == 1:
                    return f"The name is {names[0]}."
                else:
                    return f"The names mentioned are: {', '.join(names)}."

        # Quantity/Number questions
        if any(word in question_lower for word in ['how many', 'quantity', 'count', 'number of']):
            numbers = self._extract_numbers(text)
            if numbers:
                return f"The numbers mentioned are: {', '.join(numbers)}."

        return None

    def _extract_dates(self, text):
        """Extract dates using regex patterns"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if 'Date:' in pattern:
                # For labeled dates, extract the value after the label
                for match in matches:
                    dates.append(match.strip())
            else:
                dates.extend(matches)
        return list(set(dates))  # Remove duplicates

    def _extract_ids(self, text):
        """Extract IDs and codes using regex patterns"""
        ids = []
        for pattern in self.id_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if any(label in pattern for label in ['ID:', 'Code:', 'Baseline ID:', 'PBR:']):
                # For labeled IDs, extract the value after the label
                for match in matches:
                    ids.append(match.strip())
            else:
                ids.extend(matches)
        return list(set(ids))  # Remove duplicates

    def _extract_names(self, question, text):
        """Extract names and titles based on context"""
        # Look for labeled names first
        labeled_patterns = [
            r'\bProduct:\s*([^\n\r]+)',  # Product: something
            r'\bTitle:\s*([^\n\r]+)',   # Title: something
            r'\bName:\s*([^\n\r]+)'     # Name: something
        ]

        names = []
        for pattern in labeled_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.strip()
                if name and len(name) > 2:
                    names.append(name)

        # If no labeled names, look for title case phrases
        if not names:
            title_case_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'  # Multiple title case words
            matches = re.findall(title_case_pattern, text)
            for match in matches:
                if len(match) > 5 and not any(word in match.lower() for word in ['from', 'this', 'that', 'with', 'and', 'the', 'for', 'are', 'was', 'were']):
                    names.append(match)

        return list(set(names[:3]))  # Limit to 3 unique names

    def _extract_numbers(self, text):
        """Extract numbers from text"""
        numbers = []
        for pattern in self.number_patterns:
            matches = re.findall(pattern, text)
            # Filter out very common numbers like single digits
            filtered_matches = [match for match in matches if len(match) > 1 or match in ['0', '1', '2']]
            numbers.extend(filtered_matches)
        return list(set(numbers[:10]))  # Limit to 10 unique numbers

    def _split_into_sentences(self, text):
        """Split text into sentences using regex"""
        # Simple sentence splitting on periods, question marks, exclamation marks
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        # Filter out very short sentences and clean up
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences

    def _score_sentences(self, sentences, question):
        """Score sentences based on keyword overlap with question"""
        # Get question keywords (remove stop words)
        question_words = set(question.lower().split())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'what', 'where', 'when', 'why', 'how', 'who', 'which', 'that', 'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        keywords = [word for word in question_words if word not in stop_words and len(word) > 2]

        scored_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = 0

            # Exact keyword matches (highest priority)
            keyword_score = sum(1 for keyword in keywords if keyword in sentence_lower)
            score += keyword_score * 3

            # Exact phrase matches (very high priority)
            phrase_score = 0
            for i in range(len(keywords) - 1):
                phrase = f"{keywords[i]} {keywords[i+1]}"
                if phrase in sentence_lower:
                    phrase_score += 5
            score += phrase_score

            # Factual content indicators (boost score for sentences with dates, numbers, IDs)
            factual_indicators = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD dates
                r'\b\d{4,}\b',  # years or long numbers
                r'\b[A-Z]{2,}-\d{4,}\b',  # IDs like PBR-2025
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',  # title case phrases
                r'\b\d+(?:\.\d+)?\b',  # numbers
                r'\bDate:',  # Date labels
                r'\bID:',  # ID labels
                r'\bProduct:',  # Product labels
            ]

            factual_score = 0
            for pattern in factual_indicators:
                if re.search(pattern, sentence, re.IGNORECASE):
                    factual_score += 3  # Higher boost for factual content
            score += factual_score

            # Length penalty (prefer medium-length sentences)
            word_count = len(sentence.split())
            if 5 <= word_count <= 30:
                score += 1
            elif word_count > 50:
                score -= 1

            if score > 0:
                scored_sentences.append((score, sentence))

        return scored_sentences

    def _select_sentences(self, scored_sentences):
        """Select and rank sentences"""
        # Sort by score descending
        scored_sentences.sort(reverse=True, key=lambda x: x[0])

        # Take sentences with scores > 0, limit to 6
        selected = [sentence for score, sentence in scored_sentences if score > 0][:6]

        # If we have more than 3, take top 3 and bottom 3 to get variety
        if len(selected) > 3:
            selected = selected[:3] + selected[-3:] if len(selected) > 6 else selected[:3]

        return selected

    def _deduplicate_sentences(self, sentences):
        """Remove duplicate or very similar sentences"""
        filtered = []
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            is_duplicate = False
            for existing in filtered:
                existing_words = set(existing.lower().split())
                # Check if sentences share more than 70% of words
                overlap = len(sentence_words & existing_words)
                total_unique = len(sentence_words | existing_words)
                if total_unique > 0 and (overlap / total_unique) > 0.7:
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered.append(sentence)
        return filtered

class ChatInterface:
    def __init__(self):
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.answer_generator = ExtractiveAnswerGenerator()

        self.vector_store = None
        self.setup_vector_store()

    def _get_embeddings(self):
        """Lazy load embeddings to avoid import issues"""
        if self.embeddings is None:
            try:
                self.embeddings = SentenceTransformerEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load embeddings: {e}")
        return self.embeddings

    def setup_vector_store(self):
        """Initialize vector store - try to load existing one"""
        try:
            embeddings = self._get_embeddings()
            self.vector_store = FAISS.load_local("vector_store", embeddings)
        except:
            self.vector_store = None

    def build_vector_store(self, documents):
        """Build FAISS vector store from processed documents"""
        if not documents:
            return

        embeddings = self._get_embeddings()

        chunks = []
        metadatas = []

        for doc in documents:
            doc_chunks = self.text_splitter.split_text(doc["text"])
            for chunk in doc_chunks:
                chunks.append(chunk)
                metadatas.append({
                    "source": doc["source"],
                    "page": doc.get("page", 1)
                })

        if chunks:
            self.vector_store = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
            self.vector_store.save_local("vector_store")

    def get_answer(self, question):
        """Retrieve answer from vector database (RAG)"""
        if not self.vector_store:
            return {
                "response": "No documents have been processed yet. Please upload documents first.",
                "sources": []
            }

        # Retrieve relevant documents
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        retrieved_docs = retriever.get_relevant_documents(question)

        # Generate answer using extractive method
        answer = self.answer_generator.generate_answer(question, retrieved_docs)

        # Extract sources
        sources = [
            f"{doc.metadata.get('source', 'Unknown Source')} (page: {doc.metadata.get('page', 'N/A')})"
            for doc in retrieved_docs
        ]

        return {
            "response": answer,
            "sources": sources
        }
