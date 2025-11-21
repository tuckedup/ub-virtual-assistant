How to run the LLM. 

cd llama.cpp
curl -L -o mistral.gguf \
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

rm -rf build
mkdir build
cd build

cmake .. -DLLAMA_ACCELERATE=ON -DBUILD_SHARED_LIBS=OFF
cmake --build . --config Release

in bin folder

./llama-run  ../../mistral.gguf



