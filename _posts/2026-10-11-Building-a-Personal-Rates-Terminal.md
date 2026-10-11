---
layout: default
title: Building a Personal Rates Terminal in Ten Days
---

## Building a Personal Rates Terminal in Ten Days

I wanted one place to answer a question I keep asking: **why are Treasury yields moving, and what is the market pricing?** The answer is scattered across the St. Louis Fed, the Treasury, the Fed's website, the CFTC, the FDIC, the IMF, three foreign central banks and a brokerage account. So I built fintrk, a personal rates terminal that pulls all of it together, caches it and turns it into pages of charts, tables and rule-based flags. It took ten days and it is now **18,500 lines of Python** covering 18 public data sources and a brokerage API. How that worked is part of the story.

<table class="ruled">
  <tr>
    <td>What it answers</td>
    <td>What moved and how unusual it is, why long rates are moving, what the market prices for the
        Fed, who is buying Treasuries, and what is coming up.</td>
  </tr>
  <tr>
    <td>The stack</td>
    <td>Python, Streamlit, Plotly, pandas, SQLite. No database server, no front-end framework.</td>
  </tr>
  <tr>
    <td>The data</td>
    <td>18 free public sources (APIs, CSV files, a web form, a scraped website) plus live quotes,
        futures and options from my brokerage's API. Optional AI summaries, off by default.</td>
  </tr>
  <tr>
    <td>Where it runs</td>
    <td>A small cloud server, three Docker containers, no open ports. Reachable only through
        Cloudflare Access.</td>
  </tr>
  <tr>
    <td>The size</td>
    <td>93 Python files, 214 unit tests, 19 SQLite caches, 6 pages, 14 plain-language error codes.</td>
  </tr>
</table>

<figure class="chart" id="f1">
  <div class="title">How the parts fit together</div>
  <div class="sub">
    Data flows top to bottom: fetched, cached, computed, shown. Everything inside the dashed box
    runs on one server.
  </div>

  <svg viewBox="0 0 720 556" role="img" aria-label="Architecture diagram. Eighteen public data sources and the Schwab brokerage API feed fetchers that keep 19 SQLite caches. The caches feed pure analytics modules, which feed a Streamlit app with six pages. A nightly snapshot job also writes to the caches and runs hourly checks that alert through a Matrix bot. The app is reached through a cloudflared tunnel and Cloudflare Access, from a laptop or phone.">
    <defs>
      <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="var(--text-muted)"/>
      </marker>
    </defs>

    <!-- sources -->
    <rect x="20" y="10" width="680" height="104" rx="10" fill="#fff" stroke="var(--axis)"/>
    <text class="lbl-hi" x="36" y="34">Sources: 18 public, plus one brokerage API</text>
    <text class="lbl" x="36" y="56" font-size="12">FRED · U.S. Treasury · TreasuryDirect · Fiscal Data · Federal Reserve · NY Fed · CFTC</text>
    <text class="lbl" x="36" y="76" font-size="12">FDIC · OFR · IMF · TIC · Bank of England · Bundesbank · Japan MOF · Atlanta &amp; Cleveland Fed · SEC · Nasdaq</text>
    <text class="lbl" x="36" y="96" font-size="12">Schwab Trader API (OAuth): live quotes, futures, options, minute bars</text>
    <line x1="142" y1="114" x2="142" y2="163" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>

    <!-- server -->
    <rect x="20" y="128" width="680" height="262" rx="12" fill="none" stroke="var(--axis)" stroke-dasharray="5 4"/>
    <text class="tick" x="164" y="150">Server · Docker Compose · three containers · no open ports</text>

    <rect x="40" y="165" width="205" height="90" rx="8" fill="#fff" stroke="var(--series-1)" stroke-width="1.5"
          data-tip="<b>Fetchers + caches</b>One module per source. Each downloads only what is stale and falls back to its cache when the website fails."/>
    <text class="lbl-hi" x="56" y="189">Fetchers + caches</text>
    <text class="lbl" x="56" y="209" font-size="12">19 SQLite files</text>
    <text class="lbl" x="56" y="227" font-size="12">download only what's stale</text>
    <text class="lbl" x="56" y="245" font-size="12">fall back when a site fails</text>

    <line x1="245" y1="210" x2="265" y2="210" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="267" y="165" width="205" height="90" rx="8" fill="#fff" stroke="var(--series-1)" stroke-width="1.5"
          data-tip="<b>Pure analytics</b>Data in, numbers out, no user-interface code, so every model is unit-tested on synthetic data."/>
    <text class="lbl-hi" x="283" y="189">Pure analytics</text>
    <text class="lbl" x="283" y="209" font-size="12">curves, Fed path, options,</text>
    <text class="lbl" x="283" y="227" font-size="12">futures basis, flags</text>
    <text class="lbl" x="283" y="245" font-size="12">214 unit tests, no network</text>

    <line x1="472" y1="210" x2="492" y2="210" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="494" y="165" width="186" height="90" rx="8" fill="#fff" stroke="var(--series-1)" stroke-width="1.5"
          data-tip="<b>Streamlit app</b>Today, Dashboard (5 tabs), Equities, Structural, Before a trade, System status."/>
    <text class="lbl-hi" x="510" y="189">Streamlit app</text>
    <text class="lbl" x="510" y="209" font-size="12">6 pages, 5 dashboard tabs</text>
    <text class="lbl" x="510" y="227" font-size="12">every error has a code</text>
    <text class="lbl" x="510" y="245" font-size="12">and a fix-it guide</text>

    <rect x="40" y="285" width="205" height="80" rx="8" fill="#fff" stroke="var(--axis)"
          data-tip="<b>Snapshot job</b>Some brokerage data is shown only briefly (settlements, minute bars, option prices). A day not saved is gone, so a job saves it every weekday whether or not anyone opens the app."/>
    <text class="lbl-hi" x="56" y="309">Snapshot job</text>
    <text class="lbl" x="56" y="329" font-size="12">weekdays, 17:30 New York</text>
    <text class="lbl" x="56" y="347" font-size="12">saves what Schwab won't keep</text>
    <line x1="142" y1="285" x2="142" y2="257" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>

    <line x1="245" y1="325" x2="265" y2="325" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="267" y="285" width="205" height="80" rx="8" fill="#fff" stroke="var(--axis)"
          data-tip="<b>Hourly checks</b>Is the brokerage sign-in about to expire, or revoked? Did last night's snapshot come back complete?"/>
    <text class="lbl-hi" x="283" y="309">Hourly checks</text>
    <text class="lbl" x="283" y="329" font-size="12">sign-in expiring or revoked?</text>
    <text class="lbl" x="283" y="347" font-size="12">snapshot missing or partial?</text>

    <line x1="587" y1="255" x2="587" y2="283" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="494" y="285" width="186" height="80" rx="8" fill="#fff" stroke="var(--axis)"
          data-tip="<b>cloudflared tunnel</b>The tunnel dials out to Cloudflare. No port on the server is open to the internet."/>
    <text class="lbl-hi" x="510" y="309">cloudflared tunnel</text>
    <text class="lbl" x="510" y="329" font-size="12">dials out to Cloudflare;</text>
    <text class="lbl" x="510" y="347" font-size="12">nothing listens</text>

    <!-- outside -->
    <line x1="370" y1="365" x2="370" y2="408" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="267" y="410" width="205" height="60" rx="8" fill="#fff" stroke="var(--axis)"
          data-tip="<b>Matrix bot</b>Posts to a room on my own chat server, including a one-tap link to renew the brokerage sign-in."/>
    <text class="lbl-hi" x="283" y="434">Matrix bot</text>
    <text class="lbl" x="283" y="454" font-size="12">alerts + one-tap renewal link</text>

    <line x1="587" y1="365" x2="587" y2="408" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="494" y="410" width="186" height="60" rx="8" fill="#fff" stroke="var(--axis)"
          data-tip="<b>Cloudflare Access</b>Email one-time PIN, a policy for a single address, 24-hour sessions."/>
    <text class="lbl-hi" x="510" y="434">Cloudflare Access</text>
    <text class="lbl" x="510" y="454" font-size="12">one-time PIN, one address</text>

    <line x1="587" y1="470" x2="587" y2="488" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <polyline points="370,470 370,515 492,515" fill="none" stroke="var(--text-muted)" stroke-width="1.5" marker-end="url(#ah)"/>
    <rect x="494" y="490" width="186" height="50" rx="8" fill="var(--series-1)"/>
    <text x="587" y="520" text-anchor="middle" font-size="13" font-weight="700" fill="#fcfcfb">Me · laptop or phone</text>
  </svg>

  <figcaption>
    <strong>The split that matters:</strong> fetchers and analytics are plain Python modules with no
    user-interface code. Data goes in, data frames and numbers come out. That makes every pricing model,
    curve fit and date rule testable without a browser, and lets the snapshot job reuse exactly the code the
    pages use. The pages only lay things out.
  </figcaption>
</figure>

## What it does

The front door is a **Today** page: a morning view of what moved, how unusual each move is against the past year, what the market prices for the Fed, and what is due in the next two weeks. Behind it sits a **Dashboard** with five tabs grouped by question (rates and the curve, the Fed and funding, supply and demand, macro, risk and cross-asset), an **Equities** page, a **Structural** page for slow-moving fiscal and banking data, a **Before a trade** checklist and a **System status** page.

<figure class="chart" id="s1">
  <div class="title">Today: the morning view</div>
  <div class="sub">Rule-based flags, then every move with its z-score and percentile against the past year.</div>
  <img src="/img/fintrk/today.png" alt="The Today page of fintrk: flags at the top, then a table of yield and market moves with z-scores, percentiles and sparklines." style="display:block;width:100%;margin-top:16px;border:1px solid var(--border);border-radius:8px">
  <figcaption>
    Flags are heuristics with named thresholds, not signals: a move beyond two standard deviations, a curve
    inversion, funding stress, an auction that tailed, a Fed meeting this week. Each links to the chart
    with the detail.
  </figcaption>
</figure>

<figure class="chart" id="s2">
  <div class="title">Why long rates are moving</div>
  <div class="sub">The 10-year split into real yield and inflation compensation, horizon by horizon.</div>
  <img src="/img/fintrk/rates.png" alt="The Rates and curve tab: Treasury yields over time and a set of small charts splitting the 10-year move into real yield and breakeven parts." style="display:block;width:100%;margin-top:16px;border:1px solid var(--border);border-radius:8px">
  <figcaption>
    The charts follow a few fixed rules: one y-axis per chart, never two; a colourblind-validated palette in
    a fixed order; the same series always in the same colour; labels at the end of the line instead of a
    legend hunt; and a data table under every chart. The analysis in
    <a href="{% post_url 2026-10-11-It-Wasnt-the-Oil %}">It Wasn't the Oil</a> started on this tab.
  </figcaption>
</figure>

Below it sits the most desk-like feature in the app: a **trade screen** for any curve spread or butterfly on the 1- to 30-year par curve. Pick the legs, and it sizes the package the way a rates desk would.

<figure class="chart" id="s6">
  <div class="title">Any spread or butterfly, sized by risk</div>
  <div class="sub">Level, how stretched it is, what it earns while you wait, and how fast it has tended to snap back.</div>
  <img src="/img/fintrk/trade-screen.png" alt="The trade screen: a butterfly selected, with tiles for its level, z-scores, percentile, carry and rolldown, carry per unit of volatility and half-life, a history chart and a table of face amounts per leg." style="display:block;width:100%;margin-top:16px;border:1px solid var(--border);border-radius:8px">
  <figcaption>
    <strong>Sized by DV01, not by face amount.</strong> Each leg carries equal interest-rate risk, so a
    one-basis-point change in the package's level is one dollar of P&amp;L per dollar of DV01. The chart and
    the profit line up. A butterfly can be weighted 50/50, or by regression: the wings are sized from a year
    of the belly's daily moves against theirs, so the fly stops moving with the level and slope of the curve
    and isolates the curvature.
    <br><br>
    For either side of the trade the screen shows the 1- and 3-year z-score and percentile, three months of
    carry and rolldown (par bonds financed at SOFR, curve unchanged), carry per unit of volatility, a
    mean-reversion half-life from an AR(1) fit, and the face amount of each leg for a chosen DV01. These are
    the standard maturity points, not specific bonds, and a stretched z-score is a reason to look, not a
    signal.
  </figcaption>
</figure>

<figure class="chart" id="s3">
  <div class="title">What the Fed changed</div>
  <div class="sub">Any FOMC statement compared word by word with the one before.</div>
  <img src="/img/fintrk/fed-diff.png" alt="A word-by-word comparison of two FOMC statements, with deleted words struck through and new words highlighted." style="display:block;width:100%;margin-top:16px;border:1px solid var(--border);border-radius:8px">
  <figcaption>
    The Fed publishes statements and minutes as web pages, not as an API, so fintrk parses its website and
    keeps every document forever. The minutes pages changed layout around 2022 (attendance moved from the
    top to the bottom), and the parser handles both.
  </figcaption>
</figure>

## The integrations

Most of the work in a project like this isn't the charts. It's getting eighteen organisations' data into one shape. Each source gets its own fetcher and its own cache, downloads only what is stale (most every six hours, some hourly, some once per document), and falls back to the last saved copy when the website is down. A few took real work:

<table class="ruled">
  <tr>
    <td>Schwab Trader API</td>
    <td>My own OAuth client, not a library. A 30-minute access token renewed automatically and a
        7-day refresh token that renewal doesn't extend, so a fresh sign-in is due weekly. The token
        file is shared by two containers, so it is written atomically: temp file, then rename.</td>
  </tr>
  <tr>
    <td>TreasuryDirect</td>
    <td>End-of-day prices for every Treasury note and bond come from a web form with an anti-forgery
        token: fetch the page, read the token, post the date. About 465 bonds a day, priced into
        yields all at once with a vectorised solver.</td>
  </tr>
  <tr>
    <td>Futures options</td>
    <td>The brokerage has no option-chain endpoint for options on futures, so fintrk builds the
        contract symbols itself (strike grids at 1/16 points for SOFR options) and quotes them hourly.
        The quotes carry no implied volatilities, so those are computed locally.</td>
  </tr>
  <tr>
    <td>IMF</td>
    <td>The new data API returns CSV only if you ask in an HTTP header, and the full response is
        10 MB. Asking for data only cuts it to 12 KB.</td>
  </tr>
  <tr>
    <td>Japan's Ministry of Finance</td>
    <td>Weekly flows come as a CSV in a Japanese text encoding with full-width dots, and weeks
        spanning New Year repeat the year.</td>
  </tr>
  <tr>
    <td>FDIC</td>
    <td>Industry totals come from the API's aggregation mode, but adding one more aggregation
        parameter returns a server error. The per-bank dataset is 4,300 rows a quarter, so only the
        missing quarters and the latest two are re-downloaded: 7 seconds instead of 50.</td>
  </tr>
  <tr>
    <td>SEC EDGAR and Nasdaq</td>
    <td>Earnings dates for mega-cap stocks: past report times from 8-K filings (before the open or
        after the close), upcoming dates from Nasdaq's calendar, an estimate from last year when
        neither has it.</td>
  </tr>
</table>

## Things the data taught me

The best part of a project's documentation is the list of things that weren't true. fintrk's instruction file has a growing section of them, each found by checking, usually the hard way:

<table class="ruled">
  <tr>
    <td>Futures history has no months</td>
    <td>The brokerage's price-history call ignores the contract month: ask for any fed funds future
        and you get the front contract. Per-contract history exists only because fintrk saves each
        day's settlement itself, so a missed day can never be filled in later.</td>
  </tr>
  <tr>
    <td>$MOVE is not the MOVE</td>
    <td>The symbol <code>$MOVE</code> is a Northern Trust TIPS index, not the bond-volatility index of
        the same name. Bond volatility comes from options instead.</td>
  </tr>
  <tr>
    <td>Don't trust the broker's greeks</td>
    <td>Put and call implied vols at neighbouring strikes differed by about 4 points, a sign of the
        wrong forward price. fintrk computes its own vols from bid/ask mids, on the forward implied
        by put-call parity.</td>
  </tr>
  <tr>
    <td>FRED dates aren't what you asked</td>
    <td>For monthly and weekly series, FRED returns the period <em>containing</em> your start date,
        dated before it. The cache refresh clears from the earliest row returned, not from the date
        requested.</td>
  </tr>
  <tr>
    <td>Some data never arrives</td>
    <td>October 2025's CPI was never published (the government shutdown). All time math is by
        calendar date, not row position, so a missing month can't shift a year-over-year change.</td>
  </tr>
  <tr>
    <td>Some data is from the future</td>
    <td>The Fed's projections are dated by target year. Left in the daily frame, they made "today"
        three years from now. They are split off before anything else runs.</td>
  </tr>
  <tr>
    <td>Same strikes, different options</td>
    <td>On monthly expiries the S&amp;P 500 chain lists two contracts at every strike, settled on the
        morning and afternoon prices. Mixing them silently overwrote rows; only the afternoon-settled
        ones are kept.</td>
  </tr>
  <tr>
    <td>Calendars are in months</td>
    <td>Which bonds can be delivered into a Treasury future is defined in calendar months. One day
        short is out, so the eligibility rules can't use days ÷ 365.25.</td>
  </tr>
</table>

## Designing for failure

With eighteen external sources, something is always broken somewhere: a site redesigns, an API times out, a certificate expires. The rule is that **one failure never takes down a page**. A failing source shows its last saved data with a box explaining what broke. A bug in one section shows an error box, and the rest of the page renders.

Every visible error is classified into one of 14 codes: network, certificate, site down, API key, format changed, damaged cache, stale data, brokerage sign-in, crash. Each code has a matching section in a troubleshooting guide written for a non-programmer: what you see, why, numbered steps. Error messages are built without URLs, so an API key in a URL can't leak onto the screen, and the log redacts anything shaped like a token.

<figure class="chart" id="s4">
  <div class="title">System status</div>
  <div class="sub">Every source's last success, last problem and staleness, with a Retry button.</div>
  <img src="/img/fintrk/status.png" alt="The System status page: a table of data sources with their last successful update, staleness and any problem code." style="display:block;width:100%;margin-top:16px;border:1px solid var(--border);border-radius:8px">
  <figcaption>
    The page also checks the setup (which settings exist, never their values) and builds a diagnostic report
    that is safe to share because it contains no keys or tokens.
  </figcaption>
</figure>

## Running it

fintrk runs on a small cloud server as three containers from one image: the **app**, a **snapshot** job and a **tunnel**. Nothing publishes a port. The tunnel dials out to Cloudflare, and Cloudflare Access asks for a one-time PIN sent to one email address before anything reaches the app.

Two operational details I'm pleased with:

- **A missing disk fails loudly.** The data lives on its own block volume. The bare mount point underneath is made immutable, so if the volume ever fails to attach, the containers refuse to start instead of quietly starting with empty caches on the boot disk.
- **The weekly sign-in is one tap.** The brokerage sign-in lasts seven days. An hourly check notices when it's about to run out and posts a link to a room on my <a href="{% post_url 2025-12-30-Setting-Up-a-Personal-Matrix-Synapse-Chat-Server %}">own Matrix server</a>. One tap opens a sign-in page behind Cloudflare Access, the brokerage redirects back, and the app finishes the exchange by itself. A one-time state value, valid for 15 minutes, stops a forged or replayed callback. The sign-in address contains the app's key, so it is only ever built on the protected page, never put in a chat message or a log.

<figure class="chart" id="s5">
  <div class="title">The weekly renewal, from my phone</div>
  <div class="sub">The bot's reminder, and its confirmation after the one-tap sign-in.</div>
  <img src="/img/fintrk/alert.png" alt="A phone screenshot of a Matrix chat: the bot says the brokerage sign-in runs out soon, with a renewal link, then confirms the new sign-in." style="display:block;width:auto;max-width:100%;max-height:560px;margin:16px auto 0;border:1px solid var(--border);border-radius:8px">
</figure>

The snapshot job exists because some data is only shown briefly. Futures settlements, about ten days of minute bars and the option chains themselves: the brokerage keeps no history of any of them. Every weekday at 17:30 New York the job saves the S&amp;P 500 option chain, a fixed-grid volatility surface, and chains and minute bars for 22 ETFs and stocks, about 5 MB a day. It dates each snapshot by the quotes' own session, so a run on a market holiday saves nothing rather than saving yesterday twice.

## How it was built

I built fintrk with LLM assistance, which wrote the code working directly in the repository. My part was deciding what to build, setting the rules, reviewing what came back and running the server. Over ten days that settled into a working method.

**The instruction file is the spec.** The repository has a `CLAUDE.md` that the agent reads at the start of every session. It started as a page and is now 485 lines: the layout of the code, the conventions, the security rules (never read the secrets file, never print a token), and the list of facts above. Every time something turned out to be wrong, the correction went into the file, so it was never rediscovered. It's the most valuable document in the project.

**Decisions stay with me.** The plan file records each one: AI summaries off by default; currencies only as a lens on US rates; the Equities page as its own page; tone scoring on hold; the news page removed. The agent proposes and builds; what goes in, and what comes out, is mine.

**Reviews in rounds.** Several times I had the agent review the app as a rates analyst or a quant would, list what was missing or misleading, then build the fixes in batches. Those rounds produced the five-tab layout, the relative-value tools and the equity volatility work.

**Verification is part of the job.** Each change is checked four ways: unit tests on synthetic data (214 of them, no network), a headless run of every page, a real browser with every chart screenshotted and inspected (chart clipping only shows up there), and a Docker build tested on a copy of the data before it ships. The real caches are never used for fault tests.

<figure class="chart" id="f2">
  <div class="title">Ten days, first line to quant review</div>
  <div class="sub">
    Milestones from the project's plan and git history. Dated commits start on October 5, when the
    server copy was made; the first three days come from the plan.
  </div>

  <svg viewBox="0 0 720 416" role="img" aria-label="Timeline. October 2 to 4: a free-data dashboard. October 5: reviews, live brokerage data and a server copy. October 7: the Equities page, the 30-year backtest and nightly option snapshots. October 8: live on the server, with Matrix alerts and one-tap sign-in. October 11: a four-batch quant review of the Equities page.">
    <line x1="130" y1="20" x2="130" y2="400" stroke="var(--axis)" stroke-width="2"/>

    <text class="lbl-hi" x="112" y="34" text-anchor="end">Oct 2–4</text>
    <circle cx="130" cy="30" r="6" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2"/>
    <text class="lbl-hi" x="150" y="34">A free-data dashboard</text>
    <text class="lbl" x="150" y="54" font-size="12.5">FRED first, then auctions, macro, FOMC statements, the dollar, Japan, fiscal.</text>
    <text class="lbl" x="150" y="72" font-size="12.5">Today page, error codes, nowcasts, minutes, banks, oil, a volatility gauge.</text>

    <text class="lbl-hi" x="112" y="116" text-anchor="end">Oct 5</text>
    <circle cx="130" cy="112" r="6" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2"/>
    <text class="lbl-hi" x="150" y="116">Reviews, live data, a server copy</text>
    <text class="lbl" x="150" y="136" font-size="12.5">Analyst-style reviews regroup the Dashboard into five tabs; relative value.</text>
    <text class="lbl" x="150" y="154" font-size="12.5">Brokerage API: Fed path by meeting, SOFR options, event moves, futures basis.</text>

    <text class="lbl-hi" x="112" y="198" text-anchor="end">Oct 7</text>
    <circle cx="130" cy="194" r="6" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2"/>
    <text class="lbl-hi" x="150" y="198">Equities, research, storage</text>
    <text class="lbl" x="150" y="218" font-size="12.5">Equities page in four phases; the 30-year backtest; the dollar's global role.</text>
    <text class="lbl" x="150" y="236" font-size="12.5">Nightly S&amp;P 500 option snapshot; the data gets its own block volume.</text>

    <text class="lbl-hi" x="112" y="280" text-anchor="end">Oct 8</text>
    <circle cx="130" cy="276" r="8" fill="var(--series-2)" stroke="var(--surface-1)" stroke-width="2"/>
    <text class="lbl-hi" x="150" y="280">Live</text>
    <text class="lbl" x="150" y="300" font-size="12.5">Running behind Cloudflare Access; option archive for 22 ETFs and stocks.</text>
    <text class="lbl" x="150" y="318" font-size="12.5">Matrix alerts and one-tap brokerage sign-in; the architecture document.</text>

    <text class="lbl-hi" x="112" y="362" text-anchor="end">Oct 11</text>
    <circle cx="130" cy="358" r="6" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2"/>
    <text class="lbl-hi" x="150" y="362">Quant review</text>
    <text class="lbl" x="150" y="382" font-size="12.5">Variance swaps, volatility risk premium, sector correlation, a trend model,</text>
    <text class="lbl" x="150" y="400" font-size="12.5">event moves priced by S&amp;P options, mega-cap earnings: four batches.</text>
  </svg>

  <figcaption>
    No commits on October 6, 9 and 10. The server install on October 7–8 followed a step-by-step runbook
    kept in the repository, which now ends with an as-built record and the lessons from the install.
  </figcaption>
</figure>

<figure class="chart" id="f3">
  <div class="title">Where the 18,500 lines are</div>
  <div class="sub">Lines of Python by part of the project, plus the Markdown documentation for comparison.</div>

  <svg viewBox="0 0 720 360" role="img" aria-label="Bar chart of lines by area. Data and analytics: 10,804 lines of Python. Pages and user interface: 4,868. Tests: 2,298. Operations and research scripts: 489. Documentation in Markdown: 2,112.">
    <g>
      <line class="gridline" x1="230" y1="12" x2="230" y2="308"/>
      <line class="gridline" x1="298.3" y1="12" x2="298.3" y2="308"/>
      <line class="gridline" x1="366.7" y1="12" x2="366.7" y2="308"/>
      <line class="gridline" x1="435" y1="12" x2="435" y2="308"/>
      <line class="gridline" x1="503.3" y1="12" x2="503.3" y2="308"/>
      <line class="gridline" x1="571.7" y1="12" x2="571.7" y2="308"/>
      <line class="gridline" x1="640" y1="12" x2="640" y2="308"/>
    </g>
    <line class="axisline" x1="230" y1="12" x2="230" y2="308"/>
    <g class="tick" text-anchor="middle">
      <text x="230" y="328">0</text><text x="298.3" y="328">2,000</text><text x="366.7" y="328">4,000</text>
      <text x="435" y="328">6,000</text><text x="503.3" y="328">8,000</text><text x="571.7" y="328">10,000</text>
      <text x="640" y="328">12,000</text>
    </g>
    <text class="tick" x="435" y="350" text-anchor="middle">lines</text>

    <text class="lbl-hi" x="218" y="37" text-anchor="end">Data &amp; analytics</text>
    <text class="lbl" x="218" y="53" text-anchor="end" font-size="11.5">54 modules: fetchers, models, charts</text>
    <path d="M230 22 H 595.1 A 4 4 0 0 1 599.1 26 V 42 A 4 4 0 0 1 595.1 46 H 230 Z" fill="var(--series-1)"
          data-tip="<b>Data &amp; analytics</b>10,804 lines in 54 modules: one fetcher per source, the pricing and curve models, the chart builders"/>
    <text class="val" x="609" y="39">10,804</text>

    <text class="lbl" x="218" y="95" text-anchor="end">Pages &amp; interface</text>
    <text class="lbl" x="218" y="111" text-anchor="end" font-size="11.5">12 view scripts + entry point</text>
    <path d="M230 80 H 392.3 A 4 4 0 0 1 396.3 84 V 100 A 4 4 0 0 1 392.3 104 H 230 Z" fill="var(--series-1)"
          data-tip="<b>Pages &amp; interface</b>4,868 lines: page layouts, shared cached loaders, navigation"/>
    <text class="val" x="406" y="97">4,868</text>

    <text class="lbl" x="218" y="153" text-anchor="end">Tests</text>
    <text class="lbl" x="218" y="169" text-anchor="end" font-size="11.5">214 tests, synthetic data</text>
    <path d="M230 138 H 304.5 A 4 4 0 0 1 308.5 142 V 158 A 4 4 0 0 1 304.5 162 H 230 Z" fill="var(--series-1)"
          data-tip="<b>Tests</b>2,298 lines, 214 tests: pricing round trips, curve fits, date rules, parsers, the snapshot job, the sign-in pages"/>
    <text class="val" x="318" y="155">2,298</text>

    <text class="lbl" x="218" y="211" text-anchor="end">Ops &amp; research scripts</text>
    <text class="lbl" x="218" y="227" text-anchor="end" font-size="11.5">snapshot job, backtests, probes</text>
    <path d="M230 196 H 242.7 A 4 4 0 0 1 246.7 200 V 216 A 4 4 0 0 1 242.7 220 H 230 Z" fill="var(--series-1)"
          data-tip="<b>Ops &amp; research scripts</b>489 lines: the nightly snapshot service, the 30-year backtest and forecast test, API probes"/>
    <text class="val" x="257" y="213">489</text>

    <text class="lbl" x="218" y="269" text-anchor="end">Documentation</text>
    <text class="lbl" x="218" y="285" text-anchor="end" font-size="11.5">Markdown, not Python</text>
    <path d="M230 254 H 298.2 A 4 4 0 0 1 302.2 258 V 274 A 4 4 0 0 1 298.2 278 H 230 Z" fill="var(--deemph)"
          data-tip="<b>Documentation</b>2,112 lines: README, architecture, deployment runbook, troubleshooting guide, plan, and the agent's instruction file"/>
    <text class="val" x="312" y="271">2,112</text>
  </svg>

  <figcaption>
    The documentation is a working part of the system. The troubleshooting guide is what I read when a box
    appears; the deployment runbook is how the server was built; the instruction file is how the agent knows
    the rules. Line counts are of files tracked in git on October 11.
  </figcaption>

  <details>
    <summary>Table view</summary>
    <table>
      <thead><tr><th>Area</th><th>Files</th><th>Lines</th></tr></thead>
      <tbody>
        <tr><td>Data &amp; analytics (<code>fintrk/</code>)</td><td>54</td><td>10,804</td></tr>
        <tr><td>Pages &amp; interface (<code>views/</code>, <code>app.py</code>)</td><td>13</td><td>4,868</td></tr>
        <tr><td>Tests</td><td>20</td><td>2,298</td></tr>
        <tr><td>Ops &amp; research scripts</td><td>—</td><td>489</td></tr>
        <tr><td><strong>Python total</strong></td><td><strong>93</strong></td><td><strong>18,510</strong></td></tr>
        <tr><td>Documentation (Markdown)</td><td>6</td><td>2,112</td></tr>
      </tbody>
    </table>
  </details>
</figure>

## What I'd tell someone starting one

- **Write the rules down as you learn them.** The instruction file turned an agent that forgets everything between sessions into one that knows the project's history. Every hour spent on it came back.
- **Keep the decisions.** An agent will happily build everything you mention. The plan file's list of things decided against is as important as the list of things built.
- **Make failure boring.** Codes, fallbacks and a status page are cheap to build early and expensive to retrofit. A personal tool you have to debug before you can use it is a tool you stop using.
- **Check in a browser.** Tests catch wrong numbers; only a screenshot catches a clipped label. An automated layout check once passed a chart whose end label was cut off; looking at the screenshot caught it.

The next step is the one the app was built for: using it. The first piece of analysis from it is <a href="{% post_url 2026-10-11-It-Wasnt-the-Oil %}">It Wasn't the Oil</a>, on what really pushed Treasury yields up in 2026.

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
