
# Codespaces 
Utilizar 4-core • 16GB RAM • 32GB


# Crea la imagen docker con la app streamlit
docker compose build  

# Lanza los contenedores con la aplicacion y el servidor ollama
docker compose up -d


# Descargas modelos
docker exec -it ollama ollama pull qwen2.5:0.5b-instruct-q4_K_M
<!-- docker exec -it ollama ollama pull qwen3:8b -->
<!-- docker exec -it ollama ollama pull gemma3:12b -->

# Parar contenedores
docker compose down

# Parar contenedores y borrado de volumenes
docker compose down -v
