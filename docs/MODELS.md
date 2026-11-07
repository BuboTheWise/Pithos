# Models: tiers and the archive

## Principles

1. **Local and owned.** Every model runs on your hardware. No account, no API key at run time.
2. **Uncensored where it matters.** A preparedness and knowledge tool shouldn't refuse first-aid, chemistry or electrical questions. Pithos prefers uncensored builds:
   - **orcarouter** "Uncensored" releases (preferred where they exist and fit).
   - **heretic** builds (e.g. [llmfan46](https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic), made with [p-e-w/heretic](https://github.com/p-e-w/heretic)) and their **mradermacher** imatrix quants are also accepted.
   - Other abliteration families aren't in the reference list. Contributors can propose additions with benchmarks.
3. **Verified pulls only.** Where a model has no Ollama library page, Pithos uses Ollama's [Hugging Face integration](https://huggingface.co/docs/hub/ollama): `ollama pull hf.co/<repo>:<QUANT>`. Every command listed here has been checked to resolve.
4. **Fit the 13 GiB ceiling.** On a BC-250, model weights plus KV cache must stay under about 13 GiB (16 GB shared memory minus OS, N.O.M.A.D. and embeddings).

## BC-250 picks (single box)

| Role | Model | Quant | File size | Pull |
|---|---|---|---|---|
| **Fast pick** (server; also desktop if memory allows) | [mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF](https://huggingface.co/mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF) (base: llmfan46/Qwen3.6-35B-A3B-uncensored-heretic) | i1-IQ2_M | 11.66 GB | `ollama pull hf.co/mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF:i1-IQ2_M` |
| **Quality pick** (server) | [orcarouter/Qwen3.8-27B-Uncensored-GGUF](https://huggingface.co/orcarouter/Qwen3.8-27B-Uncensored-GGUF) (base: Qwen/Qwen3.8-27B) | IQ3_XXS | 11.64 GB | `ollama pull hf.co/orcarouter/Qwen3.8-27B-Uncensored-GGUF:IQ3_XXS` (**gated**, see below) |
| **Embeddings** (required by N.O.M.A.D.) | nomic-embed-text | v1.5 | small | Pulled by N.O.M.A.D. through the host Ollama |
| **Desktop small model** | **TBD**: something small enough to leave room for XFCE and a browser | | | (open decision) |

Notes:

- **The fast pick is a mixture-of-experts model (~3B active parameters)**, so it generates much faster than a dense 27B. The quality pick is dense: slower, but more capable per byte. Pithos hasn't measured either on a BC-250 yet. **[UNVERIFIED]: please contribute numbers from `tools/ollama-bench.sh`.**
- At about 11.6 GB, both picks leave little room for KV cache, so keep context modest (8-16K, q8_0 KV). If the desktop is running, the fast pick may not fit **[UNVERIFIED]**. That's why desktop mode gets its own small model.
- **The orcarouter repo is gated.** Accept its terms on Hugging Face while logged in, and add your Ollama public key to your HF account (see the [HF Ollama docs](https://huggingface.co/docs/hub/ollama)) so `ollama pull` can authenticate. Without that, the pull fails with 401. For the archive, keep the downloaded files so other boxes don't need the gate. *(Re-sharing gated weights depends on the model's license; check before redistributing.)*
- Smaller fallbacks available in the same repos: orcarouter IQ2_M (10.46 GB); mradermacher i1-IQ3_XXS (13.62 GB, which is **over** the comfortable ceiling).

## Other tiers

| Tier | Machine | Suggested |
|---|---|---|
| Cluster (2-3 BC-250s) | llama.cpp RPC | Higher-quality quants of the same families split across boxes (e.g. orcarouter Qwen3.8-27B Q4_K_M at 16.8 GB, or Q5_K_M at 19.5 GB). Adds capacity, not speed. **[UNVERIFIED]** |
| Laptop (Framework, iGPU/Vulkan) | Ollama or llama.cpp | [llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF](https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF) Q4_K_M (21.2 GB) if memory allows |
| Desktop (RTX 3090, 24 GB) | Ollama or llama.cpp | orcarouter Qwen3.8-27B-Uncensored Q4_K_S (15.8 GB) or Q4_K_M (16.8 GB) |

## The archive

Models get pulled, gated, relicensed or renamed. Hosting sites change their terms. A Pithos box should keep working, and keep its ability to **re-share**, even if the original download disappears.

**For each archived model, keep:**

```
archive/models/<publisher>/<repo>/
  <file>.gguf            # every quant you might want, not only the one you run
  README.md              # the model card, as downloaded
  LICENSE                # the license text, as downloaded
  SOURCE.txt             # source URL, commit/revision hash, download date, base model, quantizer
  SHA256SUMS             # sha256sum of every file
```

**Rules of thumb:**

- **Two copies on two different disks**, preferably in two different boxes. The cluster switch makes copying between boxes easy.
- **Keep every quant on the archive drive.** The running box only needs one, but a neighbor with different hardware may need another.
- **Check hashes** after copying, and periodically (bit rot).
- **Respect licenses.** Archiving for your own use is one thing. Re-distribution must follow each model's license. Keep the license text next to the weights so whoever inherits the drive knows the terms.
- The same approach covers knowledge content (N.O.M.A.D. ZIM files, maps): keep the source, date and hash.

Archive tooling (a `pithos-archive` helper to fetch, hash and record provenance) is on the [roadmap](ROADMAP.md) and [backlog](BACKLOG.md).
