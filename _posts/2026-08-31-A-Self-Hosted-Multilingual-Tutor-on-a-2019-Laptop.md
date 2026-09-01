---
layout: default
title: A Self-Hosted Multilingual Tutor
---

## A Self-Hosted Multilingual Tutor

No API keys, no cloud, no telemetry. A 35-billion-parameter model, speech recognition and two speech synthesisers, all served from a 2019 MacBook Pro running Linux — and reaching conversational speed by consistently choosing the option that looked slower.

The number that matters is **9.9 tokens per second**, generating on the CPU of a 2019 Intel i9. That is fast enough to hold a spoken conversation. The discrete GPU in the same machine manages 4.2. Seven languages, zero Python dependencies, 22 GB of model on disk, and nothing leaving the machine.

## What it is

An OpenAI-compatible chat endpoint on `localhost:8080` — llama.cpp in Docker serving a GGUF model — plus a spoken language tutor built on top of it. You talk; it listens, replies in the target language, corrects your grammar and tracks the vocabulary you have met but never actually produced.

<table class="ruled">
  <tr>
    <td>The stack</td>
    <td>llama.cpp (chat) · whisper.cpp (speech → text) · Piper and Kokoro
        (text → speech). Four containers, one compose file, one <code>.env</code>.</td>
  </tr>
  <tr>
    <td>The languages</td>
    <td>Spanish, French, Italian, German, Russian, Ukrainian, Polish. The
        requirement was Western European, East Asian and Slavic in one model,
        which is why it is Qwen and not Llama — Llama 3.x officially covers
        eight languages and excludes Chinese, Japanese, Korean and Russian.</td>
  </tr>
  <tr>
    <td>The tutor</td>
    <td>Records from the host microphone, transcribes, generates a reply plus
        corrections plus vocabulary in one pass, speaks the reply. Load a PDF
        with <code>/file</code> and the conversation is about that instead.</td>
  </tr>
  <tr>
    <td>The rule</td>
    <td>Every bundled script is <strong>standard library only</strong>, so the
        whole thing runs on a fresh machine with no <code>pip install</code>.
        Audio and PDF extraction shell out to system binaries
        (<code>arecord</code>, <code>aplay</code>, <code>pdftotext</code>)
        rather than pulling in a dependency tree.</td>
  </tr>
</table>

## The constraint that decided everything

A 2019 16″ MacBook Pro running Linux Mint: Core i9-9980HK (8 cores), Radeon Pro 5500M 8 GB, 64 GB of DDR4-2666. The binding constraint is not compute — it is **memory bandwidth**, about 42 GB/s. Generating a token means reading the active weights out of RAM, so throughput tracks bytes read per token and almost nothing else.

That single fact explains both surprises below, and it is why every decision here was settled by an A/B on the real machine rather than by reasoning from logs and specifications. Nearly every plausible theory turned out to be wrong.

<figure class="chart" id="f1">
  <div class="title">The GPU lost, and the bigger model won</div>
  <div class="sub">
    Generation throughput, measured on the target machine. Both results are the
    opposite of the obvious expectation.
  </div>

  <svg viewBox="0 0 720 268" role="img" aria-label="Bar chart of generation throughput. Qwen3.6-35B-A3B on CPU: 9.9 tokens per second. Qwen2.5-7B on CPU: 7.3. Qwen2.5-7B on GPU: 4.2.">
    <g>
      <line class="gridline" x1="250" y1="24" x2="250" y2="212"/>
      <line class="gridline" x1="334" y1="24" x2="334" y2="212"/>
      <line class="gridline" x1="418" y1="24" x2="418" y2="212"/>
      <line class="gridline" x1="502" y1="24" x2="502" y2="212"/>
      <line class="gridline" x1="586" y1="24" x2="586" y2="212"/>
      <line class="gridline" x1="670" y1="24" x2="670" y2="212"/>
    </g>
    <line class="axisline" x1="250" y1="212" x2="670" y2="212"/>
    <g class="tick" text-anchor="middle">
      <text x="250" y="232">0</text><text x="334" y="232">2</text>
      <text x="418" y="232">4</text><text x="502" y="232">6</text>
      <text x="586" y="232">8</text><text x="670" y="232">10</text>
    </g>
    <text class="tick" x="460" y="256" text-anchor="middle">tokens per second</text>

    <text class="lbl-hi" x="238" y="46" text-anchor="end">Qwen3.6-35B-A3B · CPU</text>
    <text class="lbl" x="238" y="62" text-anchor="end" font-size="11.5">mixture-of-experts, ~3B active</text>
    <path d="M250 40 H 641.8 A 4 4 0 0 1 645.8 44 V 60 A 4 4 0 0 1 641.8 64 H 250 Z"
          fill="var(--series-1)" data-tip="<b>Qwen3.6-35B-A3B Q4_K_M · CPU</b>9.9 tok/s — the configuration in use"/>
    <text class="val" x="657" y="57">9.9</text>

    <text class="lbl" x="238" y="112" text-anchor="end">Qwen2.5-7B · CPU</text>
    <text class="lbl" x="238" y="128" text-anchor="end" font-size="11.5">dense, 7B active</text>
    <path d="M250 106 H 552.6 A 4 4 0 0 1 556.6 110 V 126 A 4 4 0 0 1 552.6 130 H 250 Z"
          fill="var(--deemph)" data-tip="<b>Qwen2.5-7B Q4_K_M · CPU</b>7.3 tok/s — five times smaller, and slower"/>
    <text class="val" x="568" y="123">7.3</text>

    <text class="lbl" x="238" y="178" text-anchor="end">Qwen2.5-7B · GPU</text>
    <text class="lbl" x="238" y="194" text-anchor="end" font-size="11.5">Vulkan, <tspan font-family="ui-monospace, monospace">-ngl 99</tspan></text>
    <path d="M250 172 H 412.4 A 4 4 0 0 1 416.4 176 V 192 A 4 4 0 0 1 412.4 196 H 250 Z"
          fill="var(--deemph)" data-tip="<b>Qwen2.5-7B Q4_K_M · GPU (Vulkan)</b>4.2 tok/s — partial offload thrashes over PCIe"/>
    <text class="val" x="428" y="189">4.2</text>
  </svg>

  <figcaption>
    <strong>Why the 35B model is faster than the 7B:</strong> it is a
    mixture-of-experts — about 3B of its 35B parameters are active per token.
    Generation is bandwidth-bound, so speed tracks <em>active</em> parameters,
    not total size. The corollary shaped the whole setup: prefer a big model at
    low quantisation over a small one at high, because bytes read per token is
    the thing that costs.
    <br><br>
    <strong>Why the GPU loses:</strong> <code>-ngl 99</code> allocates only about
    3.6 GiB of the 7.25 GiB free, so the model is split between CPU and GPU and
    thrashes across PCIe. Why it under-allocates is still open.
  </figcaption>

  <details>
    <summary>Table view</summary>
    <table>
      <thead><tr><th>Configuration</th><th>Quantisation</th><th>tok/s</th></tr></thead>
      <tbody>
        <tr><td>Qwen3.6-35B-A3B · CPU</td><td>UD-Q4_K_M</td><td>9.9</td></tr>
        <tr><td>Qwen2.5-7B · CPU</td><td>Q4_K_M</td><td>7.3</td></tr>
        <tr><td>Qwen2.5-7B · GPU (Vulkan)</td><td>Q4_K_M</td><td>4.2</td></tr>
      </tbody>
    </table>
  </details>
</figure>

<figure class="chart" id="f2">
  <div class="title">Where a spoken turn goes</div>
  <div class="sub">
    The current model reasons before answering. It is better for it — and it
    triples the wait, which is fatal for conversation practice.
  </div>

  <svg viewBox="0 0 720 236" role="img" aria-label="Stacked bar chart of turn latency. With reasoning disabled a turn takes about 8.5 seconds. With reasoning enabled, about 21.5 seconds, of which 13 seconds is the reasoning phase.">
    <g>
      <line class="gridline" x1="200" y1="20" x2="200" y2="164"/>
      <line class="gridline" x1="300" y1="20" x2="300" y2="164"/>
      <line class="gridline" x1="400" y1="20" x2="400" y2="164"/>
      <line class="gridline" x1="500" y1="20" x2="500" y2="164"/>
      <line class="gridline" x1="600" y1="20" x2="600" y2="164"/>
      <line class="gridline" x1="700" y1="20" x2="700" y2="164"/>
    </g>
    <line class="axisline" x1="200" y1="164" x2="700" y2="164"/>
    <g class="tick" text-anchor="middle">
      <text x="200" y="184">0</text><text x="300" y="184">5</text>
      <text x="400" y="184">10</text><text x="500" y="184">15</text>
      <text x="600" y="184">20</text><text x="700" y="184">25</text>
    </g>
    <text class="tick" x="450" y="208" text-anchor="middle">seconds per turn</text>

    <text class="lbl-hi" x="188" y="52" text-anchor="end">Reasoning off</text>
    <text class="lbl" x="188" y="68" text-anchor="end" font-size="11.5">the default</text>
    <rect x="200" y="38" width="40"  height="26" fill="var(--series-1)" data-tip="<b>Transcription</b>whisper.cpp · ~1–3 s"/>
    <rect x="242" y="38" width="98"  height="26" fill="var(--series-2)" data-tip="<b>Generation</b>llama.cpp · ~5 s"/>
    <rect x="342" y="38" width="28"  height="26" fill="var(--series-3)" data-tip="<b>Speech synthesis</b>Piper or Kokoro · ~1–2 s"/>
    <text class="val" x="384" y="56">8.5 s</text>

    <text class="lbl" x="188" y="120" text-anchor="end">Reasoning on</text>
    <text class="lbl" x="188" y="136" text-anchor="end" font-size="11.5"><tspan font-family="ui-monospace, monospace">--keep-think</tspan></text>
    <rect x="200" y="106" width="40"  height="26" fill="var(--series-1)" data-tip="<b>Transcription</b>whisper.cpp · ~1–3 s"/>
    <rect x="242" y="106" width="258" height="26" fill="var(--series-4)" data-tip="<b>Reasoning</b>~13 s before the first visible token"/>
    <text class="val-in" x="371" y="124" text-anchor="middle" fill="#0b0b0b">13 s of thinking</text>
    <rect x="502" y="106" width="98"  height="26" fill="var(--series-2)" data-tip="<b>Generation</b>llama.cpp · ~5 s"/>
    <rect x="602" y="106" width="28"  height="26" fill="var(--series-3)" data-tip="<b>Speech synthesis</b>Piper or Kokoro · ~1–2 s"/>
    <text class="val" x="644" y="124">21.5 s</text>
  </svg>

  <div class="legend">
    <span><i style="background:var(--series-1)"></i>Transcription</span>
    <span><i style="background:var(--series-4)"></i>Reasoning</span>
    <span><i style="background:var(--series-2)"></i>Generation</span>
    <span><i style="background:var(--series-3)"></i>Speech synthesis</span>
  </div>

  <figcaption>
    Reasoning is therefore off by default in the tutor and on by default in the
    plain chat client — the same server, switched <em>per request</em>. That
    detail was itself a measurement: against a server started with thinking
    disabled, a request asking for it back returned 830 characters of reasoning.
    Request-level settings win, so the server is left neutral.
    <br><br>
    Approximate: component times are the typical ranges from the project README,
    not a single timed run. The 13-second reasoning phase is measured.
  </figcaption>

  <details>
    <summary>Table view</summary>
    <table>
      <thead><tr><th>Stage</th><th>Reasoning off</th><th>Reasoning on</th></tr></thead>
      <tbody>
        <tr><td>Transcription</td><td>2.0 s</td><td>2.0 s</td></tr>
        <tr><td>Reasoning</td><td>—</td><td>13.0 s</td></tr>
        <tr><td>Generation</td><td>5.0 s</td><td>5.0 s</td></tr>
        <tr><td>Speech synthesis</td><td>1.5 s</td><td>1.5 s</td></tr>
        <tr><td><strong>Total</strong></td><td><strong>8.5 s</strong></td><td><strong>21.5 s</strong></td></tr>
      </tbody>
    </table>
  </details>
</figure>

## Reading poetry without destroying it

Loading a PDF into the conversation raised a problem that looked trivial and was not. In prose a line break belongs to the typesetter and should be folded away; in verse it belongs to the poet and folding it away destroys the material. The extractor has to decide which it is looking at, from nothing but the shape of the text.

The obvious measurement is the share of lines shorter than 55 characters — wrapped prose fills to the margin, verse does not. It works, until prose is set narrow. The same Russian passage wrapped at 55 columns scores 0.81, above any threshold that still catches the Pushkin anthology at 0.98.

<figure class="chart" id="f3">
  <div class="title">Two measurements, because one is not enough</div>
  <div class="sub">
    Every sample the detector was tested against, plotted on the two signals it
    actually uses. The shaded regions are the decision rule.
  </div>

  <svg viewBox="0 0 720 430" role="img" aria-label="Scatter plot of verse detection. Short-line share on the x-axis, median over 90th-percentile line length on the y-axis, with shaded decision regions. Seven samples: the Pushkin anthology and a sonnet classify as verse; four wrapped-prose samples and a dialogue-heavy sample classify as prose.">
    <rect x="70" y="40" width="465" height="310" fill="var(--series-2)" opacity="0.07"/>
    <rect x="535" y="40" width="93"  height="46.5" fill="var(--series-2)" opacity="0.07"/>
    <rect x="535" y="86.5" width="93" height="263.5" fill="var(--series-1)" opacity="0.09"/>
    <rect x="628" y="40" width="62"  height="310" fill="var(--series-1)" opacity="0.09"/>
    <line x1="535" y1="40" x2="535" y2="350" stroke="var(--axis)" stroke-width="1"/>
    <line x1="628" y1="40" x2="628" y2="350" stroke="var(--axis)" stroke-width="1"/>
    <line x1="535" y1="86.5" x2="628" y2="86.5" stroke="var(--axis)" stroke-width="1"/>

    <text class="anno" x="535" y="32" text-anchor="middle">0.75</text>
    <text class="anno" x="628" y="32" text-anchor="middle">0.90</text>
    <text class="anno" x="634" y="90">0.85</text>
    <text class="anno" x="302" y="340" text-anchor="middle">prose</text>
    <text class="anno" x="659" y="340" text-anchor="middle">verse</text>

    <line class="axisline" x1="70" y1="350" x2="690" y2="350"/>
    <line class="axisline" x1="70" y1="40"  x2="70"  y2="350"/>
    <g class="tick" text-anchor="middle">
      <text x="70"  y="370">0</text><text x="194" y="370">0.2</text>
      <text x="318" y="370">0.4</text><text x="442" y="370">0.6</text>
      <text x="566" y="370">0.8</text><text x="690" y="370">1.0</text>
    </g>
    <text class="tick" x="380" y="398" text-anchor="middle">share of lines under 55 characters</text>
    <g class="tick" text-anchor="end">
      <text x="58" y="354">0</text><text x="58" y="292">0.2</text>
      <text x="58" y="230">0.4</text><text x="58" y="168">0.6</text>
      <text x="58" y="106">0.8</text><text x="58" y="44">1.0</text>
    </g>
    <text class="tick" x="20" y="195" text-anchor="middle" transform="rotate(-90 20 195)">median ÷ 90th-percentile line length</text>

    <g fill="var(--series-2)" stroke="var(--surface-1)" stroke-width="2">
      <circle cx="70"    cy="51.8"  r="5.5" data-tip="<b>Prose wrapped at 80 cols</b>short-line share 0.000 · med/p90 0.962<br>→ prose"/>
      <circle cx="81.8"  cy="53.0"  r="5.5" data-tip="<b>Prose wrapped at 72 cols</b>short-line share 0.019 · med/p90 0.958<br>→ prose"/>
      <circle cx="91.1"  cy="54.6"  r="5.5" data-tip="<b>Prose wrapped at 64 cols</b>short-line share 0.034 · med/p90 0.953<br>→ prose"/>
      <circle cx="457.5" cy="258.0" r="5.5" data-tip="<b>Dialogue-heavy prose</b>short-line share 0.625 · med/p90 0.297<br>→ prose"/>
      <circle cx="571.6" cy="51.2"  r="6.5" data-tip="<b>Prose wrapped at 55 cols</b>short-line share 0.809 · med/p90 0.964<br>→ prose, and only the second measurement saves it"/>
    </g>
    <g fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2">
      <circle cx="677.6" cy="126.2" r="6.5" data-tip="<b>Pushkin anthology (the real PDF)</b>short-line share 0.980 · med/p90 0.722<br>→ verse"/>
      <circle cx="690"   cy="68.2"  r="6.5" data-tip="<b>Sonnet — regular metre</b>short-line share 1.000 · med/p90 0.909<br>→ verse, on the first measurement alone"/>
    </g>

    <line x1="97" y1="66" x2="120" y2="96" stroke="var(--axis)" stroke-width="1"/>
    <text class="anno" x="124" y="100">prose at 64 / 72 / 80 columns</text>

    <line x1="563" y1="51" x2="500" y2="51" stroke="var(--axis)" stroke-width="1"/>
    <text class="anno" x="496" y="55" text-anchor="end">narrow-set prose — only the tie-break saves it</text>

    <line x1="683" y1="74" x2="640" y2="104" stroke="var(--axis)" stroke-width="1"/>
    <text class="anno" x="636" y="108" text-anchor="end">sonnet — kept by the 0.90 shortcut</text>

    <line x1="671" y1="126" x2="628" y2="140" stroke="var(--axis)" stroke-width="1"/>
    <text class="anno" x="624" y="144" text-anchor="end">Pushkin anthology — the real book</text>

    <text class="anno" x="468" y="262">dialogue-heavy prose</text>
  </svg>

  <div class="legend">
    <span><i style="background:var(--series-1)"></i>Classified as verse</span>
    <span><i style="background:var(--series-2)"></i>Classified as prose</span>
  </div>

  <figcaption>
    The second measurement asks directly whether the lines fill to a margin.
    Wrapped prose sits at 0.95–0.96 whatever width it is set to; the Pushkin file
    sits at 0.72. That separates the ambiguous band cleanly — but it cannot be
    applied everywhere, because <strong>regular metrical verse is statistically
    identical to narrow-set prose</strong> under it. The sonnet at (1.00, 0.91)
    is the proof: judged on the tie-break it would be called prose. So above a
    0.90 short-line share the first measurement decides alone.
    <br><br>
    The bias throughout is toward answering <em>verse</em>. Reading verse as
    prose folds the line breaks away and destroys the text; reading prose as
    verse leaves it ragged, says so in the summary, and is undone by reloading.
  </figcaption>

  <details>
    <summary>Table view</summary>
    <table>
      <thead><tr><th>Sample</th><th>Lines</th><th>Short-line share</th><th>Median ÷ p90</th><th>Verdict</th></tr></thead>
      <tbody>
        <tr><td>Pushkin anthology (PDF)</td><td>1,115</td><td>0.980</td><td>0.722</td><td>verse</td></tr>
        <tr><td>Sonnet (metrical verse)</td><td>56</td><td>1.000</td><td>0.909</td><td>verse</td></tr>
        <tr><td>Prose wrapped at 55</td><td>68</td><td>0.809</td><td>0.964</td><td>prose</td></tr>
        <tr><td>Prose wrapped at 64</td><td>59</td><td>0.034</td><td>0.953</td><td>prose</td></tr>
        <tr><td>Prose wrapped at 72</td><td>52</td><td>0.019</td><td>0.958</td><td>prose</td></tr>
        <tr><td>Prose wrapped at 80</td><td>47</td><td>0.000</td><td>0.962</td><td>prose</td></tr>
        <tr><td>Dialogue-heavy prose</td><td>64</td><td>0.625</td><td>0.297</td><td>prose</td></tr>
      </tbody>
    </table>
  </details>
</figure>

<figure class="chart" id="f4">
  <div class="title">How much of a book fits in the window</div>
  <div class="sub">
    The Pushkin anthology — 39 pages, 21 poems — split into sections that fit
    alongside the conversation, at each context size.
  </div>

  <svg viewBox="0 0 720 300" role="img" aria-label="Column chart of section count against context window size. At 4096 tokens the document splits into 9 sections; at 8192 and 12288 into 2; at 16384, 24576 and 32768 into a single section.">
    <g>
      <line class="gridline" x1="70" y1="212" x2="700" y2="212"/>
      <line class="gridline" x1="70" y1="164" x2="700" y2="164"/>
      <line class="gridline" x1="70" y1="116" x2="700" y2="116"/>
      <line class="gridline" x1="70" y1="68"  x2="700" y2="68"/>
      <line class="gridline" x1="70" y1="20"  x2="700" y2="20"/>
    </g>
    <line class="axisline" x1="70" y1="212" x2="700" y2="212"/>
    <g class="tick" text-anchor="end">
      <text x="58" y="216">0</text><text x="58" y="168">2</text>
      <text x="58" y="120">4</text><text x="58" y="72">6</text>
      <text x="58" y="24">8</text>
    </g>
    <text class="tick" x="22" y="116" text-anchor="middle" transform="rotate(-90 22 116)">sections</text>

    <path d="M111 212 V 24 A 4 4 0 0 1 115 20 H 131 A 4 4 0 0 1 135 24 V 212 Z"
          fill="var(--deemph)" data-tip="<b>CTX_SIZE 4,096</b>9 sections · 555 words each on average"/>
    <text class="val" x="123" y="12" text-anchor="middle">9</text>

    <path d="M216 212 V 164 A 4 4 0 0 1 220 160 H 236 A 4 4 0 0 1 240 164 V 212 Z"
          fill="var(--deemph)" data-tip="<b>CTX_SIZE 8,192</b>2 sections · 2,498 words each"/>
    <text class="val" x="228" y="152" text-anchor="middle">2</text>

    <path d="M321 212 V 164 A 4 4 0 0 1 325 160 H 341 A 4 4 0 0 1 345 164 V 212 Z"
          fill="var(--deemph)" data-tip="<b>CTX_SIZE 12,288</b>2 sections · 2,498 words each"/>
    <text class="val" x="333" y="152" text-anchor="middle">2</text>

    <path d="M426 212 V 188 A 4 4 0 0 1 430 184 H 446 A 4 4 0 0 1 450 188 V 212 Z"
          fill="var(--series-1)" data-tip="<b>CTX_SIZE 16,384 — the setting in use</b>1 section · all 4,997 words at once"/>
    <text class="val" x="438" y="176" text-anchor="middle">1</text>

    <path d="M531 212 V 188 A 4 4 0 0 1 535 184 H 551 A 4 4 0 0 1 555 188 V 212 Z"
          fill="var(--deemph)" data-tip="<b>CTX_SIZE 24,576</b>1 section · all 4,997 words at once"/>
    <text class="val" x="543" y="176" text-anchor="middle">1</text>

    <path d="M636 212 V 188 A 4 4 0 0 1 640 184 H 656 A 4 4 0 0 1 660 188 V 212 Z"
          fill="var(--deemph)" data-tip="<b>CTX_SIZE 32,768</b>1 section · all 4,997 words at once"/>
    <text class="val" x="648" y="176" text-anchor="middle">1</text>

    <g class="tick" text-anchor="middle">
      <text x="123" y="232">4,096</text><text x="228" y="232">8,192</text>
      <text x="333" y="232">12,288</text><text x="438" y="232" fill="var(--text-primary)" font-weight="620">16,384</text>
      <text x="543" y="232">24,576</text><text x="648" y="232">32,768</text>
    </g>
    <text class="tick" x="385" y="258" text-anchor="middle">context window (tokens)</text>
    <line x1="466" y1="102" x2="454" y2="180" stroke="var(--axis)" stroke-width="1"/>
    <text class="anno" x="470" y="96">16,384 — the setting in use:</text>
    <text class="anno" x="470" y="111">the whole book in one section</text>
  </svg>

  <figcaption>
    Sizing is measured rather than assumed: the loader asks llama-server for its
    real context size and tokenises the document's own text to get
    characters-per-token for that language. It samples three spans rather than
    the opening, because books do not start in their own language — this one
    opens with an English title page, and English runs about 4 characters per
    token against Russian's 3. Measuring only the opening reports a ratio that
    is too high, which builds sections that overflow the window. That is the one
    error direction that fails silently.
    <br><br>
    The curve is also a caution. Past about 16k the document stops being split
    at all, and "discuss this passage" quietly becomes "discuss this anthology."
    <br><br>
    Computed on this machine from the real PDF, at 3.0 characters per token. The
    one point with independent ground truth — 16,384 → a single 4,997-word
    section — matches the live run exactly.
  </figcaption>

  <details>
    <summary>Table view</summary>
    <table>
      <thead><tr><th>Context window</th><th>Budget (tokens)</th><th>Sections</th><th>Mean words</th><th>Largest</th></tr></thead>
      <tbody>
        <tr><td>4,096</td><td>1,396</td><td>9</td><td>555</td><td>674</td></tr>
        <tr><td>8,192</td><td>5,492</td><td>2</td><td>2,498</td><td>2,532</td></tr>
        <tr><td>12,288</td><td>9,588</td><td>2</td><td>2,498</td><td>2,716</td></tr>
        <tr><td>16,384</td><td>13,684</td><td>1</td><td>4,997</td><td>4,997</td></tr>
        <tr><td>24,576</td><td>21,876</td><td>1</td><td>4,997</td><td>4,997</td></tr>
        <tr><td>32,768</td><td>30,068</td><td>1</td><td>4,997</td><td>4,997</td></tr>
      </tbody>
    </table>
  </details>
</figure>

<figure class="chart" id="f5">
  <div class="title">The tokeniser was part of the model choice</div>
  <div class="sub">
    Characters per token — higher is better, because it means the same passage
    costs fewer tokens of a fixed window.
  </div>

  <svg viewBox="0 0 720 190" role="img" aria-label="Dumbbell chart. Ukrainian improves from 2.03 to 3.11 characters per token between Qwen2.5 and Qwen3.6. Japanese improves from 1.25 to 1.67.">
    <g>
      <line class="gridline" x1="180" y1="24" x2="180" y2="118"/>
      <line class="gridline" x1="320" y1="24" x2="320" y2="118"/>
      <line class="gridline" x1="460" y1="24" x2="460" y2="118"/>
      <line class="gridline" x1="600" y1="24" x2="600" y2="118"/>
    </g>
    <line class="axisline" x1="180" y1="118" x2="620" y2="118"/>
    <g class="tick" text-anchor="middle">
      <text x="180" y="138">1.0</text><text x="320" y="138">2.0</text>
      <text x="460" y="138">3.0</text><text x="600" y="138">4.0</text>
    </g>
    <text class="tick" x="425" y="162" text-anchor="middle">characters per token</text>

    <text class="lbl" x="168" y="50" text-anchor="end">Ukrainian</text>
    <line x1="324.2" y1="45" x2="475.4" y2="45" stroke="var(--seq-450)" stroke-width="2" stroke-linecap="round"/>
    <circle cx="324.2" cy="45" r="6" fill="var(--seq-250)" stroke="var(--surface-1)" stroke-width="2"
            data-tip="<b>Ukrainian · Qwen2.5</b>2.03 characters per token"/>
    <circle cx="475.4" cy="45" r="6" fill="var(--seq-450)" stroke="var(--surface-1)" stroke-width="2"
            data-tip="<b>Ukrainian · Qwen3.6</b>3.11 characters per token — 53% more text per token"/>
    <text class="lbl" x="316" y="50" text-anchor="end">2.03</text>
    <text class="val" x="492" y="50">3.11</text>

    <text class="lbl" x="168" y="100" text-anchor="end">Japanese</text>
    <line x1="215" y1="95" x2="273.8" y2="95" stroke="var(--seq-450)" stroke-width="2" stroke-linecap="round"/>
    <circle cx="215"   cy="95" r="6" fill="var(--seq-250)" stroke="var(--surface-1)" stroke-width="2"
            data-tip="<b>Japanese · Qwen2.5</b>1.25 characters per token"/>
    <circle cx="273.8" cy="95" r="6" fill="var(--seq-450)" stroke="var(--surface-1)" stroke-width="2"
            data-tip="<b>Japanese · Qwen3.6</b>1.67 characters per token — 34% more text per token"/>
    <text class="lbl" x="207" y="100" text-anchor="end">1.25</text>
    <text class="val" x="290" y="100">1.67</text>
  </svg>

  <div class="legend">
    <span><i style="background:var(--seq-250)"></i>Qwen2.5</span>
    <span><i style="background:var(--seq-450)"></i>Qwen3.6 (in use)</span>
  </div>

  <figcaption>
    A better tokeniser is a larger effective context window at no cost in memory
    or speed. For non-Latin scripts this matters more than it sounds: at 2.03
    characters per token, a Ukrainian passage costs half again as many tokens as
    the same passage does under the current model.
  </figcaption>

  <details>
    <summary>Table view</summary>
    <table>
      <thead><tr><th>Language</th><th>Qwen2.5</th><th>Qwen3.6</th><th>Change</th></tr></thead>
      <tbody>
        <tr><td>Ukrainian</td><td>2.03</td><td>3.11</td><td>+53%</td></tr>
        <tr><td>Japanese</td><td>1.25</td><td>1.67</td><td>+34%</td></tr>
      </tbody>
    </table>
  </details>
</figure>

## What we ruled out, and how

The list matters as much as the results. Each of these was a plausible theory that cost time, and each was closed by a direct test rather than by argument.

<table class="ruled">
  <tr><td>ROCm for the GPU</td>
      <td>No support for <code>gfx1012</code> (RDNA1). A dead end, not a
          configuration problem. Vulkan does not use ROCm and works on this card.</td></tr>
  <tr><td>"The GPU is broken"</td>
      <td>It is not. The driver binds, the card enumerates from inside the
          container, VRAM allocates. It works — it is simply slower than the CPU.</td></tr>
  <tr><td>Docker as the bottleneck</td>
      <td>Native Docker Engine passes the render nodes straight through with no
          VM. (Docker <em>Desktop</em> on Linux does run a VM, and fails outright.)</td></tr>
  <tr><td>Flash attention</td>
      <td>On and off both give 4.2 tok/s. RDNA1 predates the cooperative-matrix
          extension it needs.</td></tr>
  <tr><td>Wrong Vulkan device</td>
      <td>Verified with <code>--list-devices</code> both ways: the discrete card
          was correctly pinned all along.</td></tr>
  <tr><td>macOS instead of Linux</td>
      <td>Metal is documented to produce garbage output on AMD discrete GPUs.
          The only working path there is the same Vulkan backend plus a
          translation layer.</td></tr>
</table>

## Things that only show up in use

Most of the interesting failures were not performance problems. They were the kind that only appear once a real person is talking to the thing.

- **Whisper does not return silence.** Given room noise it invents subtitle boilerplate absorbed from its training data. In one Russian session «Продолжение следует…» — "to be continued" — arrived twice at full speaking volume, entered the history as a real turn, and became that session's *only* correction, with the tutor gravely advising the learner that the phrase is unusual in conversation.
- **Speech recognition hides the learner's mistakes.** Whisper is trained to produce fluent text, so it transcribes what you *meant*. The tutor then sees a clean sentence and has nothing to correct. This is inherent to building on ASR and is documented as a limit rather than papered over.
- **A four-line paste became four separate turns**, each answered as a fresh question at about 25 seconds apiece — because `input()` returns one line and the next call eats the second.
- **Placeholders get copied verbatim.** Given an angle-bracket template the model reproduced it literally, so replies began "&lt;your reply, in Spanish only…&gt;" — and were spoken aloud. It gets a worked example now, with nothing bracket-shaped anywhere in the prompt.
- **A long passage pushes the rules out of the middle.** With the whole anthology loaded, the reply section came back empty on two turns of six, one reply arrived in English at a level where English is never permitted, and one "correction" replaced the learner's own sentence with a quotation from the poem. The fix was not to move the passage — that would cost the prompt cache — but to restate the rules at the very end, where attention is strongest and the tokens are already being reprocessed.

## How the numbers here were produced

The throughput, VRAM and tokenizer figures were measured on the target machine and are quoted from the project's own notes. The verse-detection and sectioning figures were computed by running the real code against the real PDF.

Where a number is an estimate rather than a measurement — the per-stage turn latencies, the characters-per-token assumption in the sectioning chart — the chart says so underneath it.

<script>
(function () {
	// Chart tooltips. Purely a mouse enhancement: each <svg> carries role="img"
	// with a full text description, and every value also appears in that
	// figure's table view, so nothing here is gated behind hover.
	if (!document.querySelector('[data-tip]')) return;

	var tip = document.createElement('div');
	tip.id = 'tip';
	tip.setAttribute('role', 'status');
	document.body.appendChild(tip);

	function show(el, x, y) {
		tip.innerHTML = el.getAttribute('data-tip').replace(/<\/b>/, '</b><br>');
		tip.style.opacity = '1';
		var r = tip.getBoundingClientRect();
		tip.style.left = Math.min(Math.max(8, x + 14), window.innerWidth - r.width - 8) + 'px';
		var top = y - r.height - 14;
		tip.style.top = (top < 8 ? y + 20 : top) + 'px';
	}
	function hide() { tip.style.opacity = '0'; }

	document.addEventListener('mousemove', function (e) {
		var el = e.target.closest ? e.target.closest('[data-tip]') : null;
		if (el) { show(el, e.clientX, e.clientY); } else { hide(); }
	});
	window.addEventListener('scroll', hide, { passive: true });
}());
</script>
