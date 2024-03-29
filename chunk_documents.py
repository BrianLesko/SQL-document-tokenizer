# Brian lesko 

# Chunk documents into smaller pieces, but keep sentences intact. 

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

def chunk_document(tokens, min_chunk_size, max_chunk_size):
    document_chunks = []
    start_index = 0
    last_sentence_end_index = 0 # to overlap sentences

    while start_index < len(tokens):
        # Get a chunk starting from the current start_index
        chunk, end_index, last_sentence_end_index= create_chunk(tokens[start_index:], min_chunk_size, max_chunk_size, last_sentence_end_index)
        
        # Add the chunk to the list
        document_chunks.append(chunk)

        # Update the start index for the next chunk
        start_index += end_index - last_sentence_end_index

        # Check if we have reached the end of the tokens
        if end_index == 0:
            break

    return document_chunks

# Helper function to create a chunk
def create_chunk(tokens, min_chunk_size, max_chunk_size, last_sentence_end_index):
    chunk = []
    end_index = 0
    sentence_end_index = 0

    for index, token in enumerate(tokens):
        chunk.append(token)
        if len(chunk) >= min_chunk_size:
            if token == '.':
                sentence_end_index = index + 1
                if len(chunk) >= min_chunk_size:
                    end_index = index + 1
                    last_sentence_end_index = sentence_end_index
                    break
            elif len(chunk) >= max_chunk_size:
                end_index = index + 1
                break

    chunk_ids = tokenizer.convert_tokens_to_ids(chunk)
    chunk_text = tokenizer.decode(chunk_ids)

    return chunk_text, end_index, last_sentence_end_index

