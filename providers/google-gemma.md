# Google Gemma key (UNRESOLVED)

**Key:** `GEMMA_API_KEY` in `runner/.env` — value `AQ.Ab8RN6...` provided by owner 2026-08-23.
Owner states it is a **Gemma API key**, not Gemini.

## Tested endpoints (all HTTP 401 UNAUTHENTICATED, 2026-08-23)
- `generativelanguage.googleapis.com/v1beta/models` + `x-goog-api-key`
- `generativelanguage.googleapis.com/v1beta/models` + `Authorization: Bearer`
- `.../v1beta/openai/models` + Bearer
- `.../v1beta/models?key=`
- `.../v1beta/models/gemma-3-27b-it:generateContent` + x-goog-api-key

## Diagnosis
`AQ.` prefix = Google OAuth2 access token format. These expire within hours and are NOT
API keys. AI Studio API keys start with `AIza`. If the owner exported this from AI Studio
"Get API key", it may have been copied from an OAuth playground instead.

## Next step
Ask owner for either:
1. An `AIza...` key from https://aistudio.google.com/apikey, or
2. The exact endpoint/base URL the Gemma key is meant for (maybe a Gemma-specific proxy).
