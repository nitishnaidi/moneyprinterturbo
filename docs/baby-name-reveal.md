# Baby Name Reveal Template

Deterministic 16:9 cinematic reveal for:

- Father: `NITISH`
- Mother: `SNEHANKITHA`
- Toddler: `ITIKA`
- Pairings: `N → SNE`, `S → HAN`, `H → ITH`

Critical text is rendered with Pillow rather than an AI video model, preventing spelling drift.

## Render

```bash
python -m app.services.baby_name_reveal --output baby-name-reveal.mp4
```

Default output is 1920x1080, 30 FPS, 9.5 seconds, H.264. The renderer uses the project's existing MoviePy/FFmpeg stack and requires no TTS or external video provider.

## Timeline

- 0.0–2.25s: parents' labels and exact names
- 2.05–3.60s: N → SNE
- 3.55–5.10s: S → HAN
- 5.05–6.60s: H → ITH
- 6.65–9.50s: individual letters converge into ITIKA, followed by the closing line

The module is intentionally isolated from the normal MoneyPrinterTurbo task pipeline so it can later be exposed as a reusable template without changing existing generation behavior.
