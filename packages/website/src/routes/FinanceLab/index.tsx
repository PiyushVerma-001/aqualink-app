import React, { useEffect, useMemo, useState } from 'react';
import './styles.css';

type Tab = 'OVERVIEW' | 'EQUITIES' | 'PORTFOLIO' | 'MACRO / FX' | 'FUNDS';

type MarketRow = {
  symbol: string;
  name: string;
  price: string;
  change: number;
  volume: string;
  spark: number[];
};

const marketRows: MarketRow[] = [
  {
    symbol: 'RELIANCE IN',
    name: 'Reliance Industries',
    price: '1,438.70',
    change: 1.84,
    volume: '12.8M',
    spark: [22, 28, 24, 35, 31, 46, 42, 53, 49, 62],
  },
  {
    symbol: 'HDFCB IN',
    name: 'HDFC Bank',
    price: '1,927.40',
    change: 0.62,
    volume: '8.4M',
    spark: [42, 38, 45, 43, 51, 49, 57, 54, 60, 66],
  },
  {
    symbol: 'INFO IN',
    name: 'Infosys',
    price: '1,472.80',
    change: -0.91,
    volume: '6.1M',
    spark: [68, 62, 65, 56, 59, 50, 53, 45, 48, 40],
  },
  {
    symbol: 'LT IN',
    name: 'Larsen & Toubro',
    price: '3,842.10',
    change: 2.17,
    volume: '2.9M',
    spark: [18, 25, 23, 37, 34, 48, 52, 50, 66, 72],
  },
  {
    symbol: 'SUNP IN',
    name: 'Sun Pharma',
    price: '1,706.30',
    change: -0.34,
    volume: '3.5M',
    spark: [56, 52, 58, 54, 48, 51, 45, 43, 47, 41],
  },
];

const news = [
  {
    time: '14:28',
    tag: 'INDIA',
    headline: 'Domestic cyclicals lead as infrastructure orders accelerate',
  },
  {
    time: '13:54',
    tag: 'ENERGY',
    headline: 'Brent holds above $71; refiners track narrower crack spreads',
  },
  {
    time: '12:36',
    tag: 'FX',
    headline: 'Rupee steadies near 83.70 as portfolio inflows offset oil demand',
  },
  {
    time: '11:08',
    tag: 'RATES',
    headline: 'India 10-year yield slips 3 bps after softer inflation print',
  },
];

const allocation = [
  { name: 'Reliance', weight: 21.4, color: '#ff9f1c' },
  { name: 'HDFC Bank', weight: 19.8, color: '#42c9b5' },
  { name: 'Infosys', weight: 18.2, color: '#44a3ff' },
  { name: 'L&T', weight: 22.6, color: '#ffd166' },
  { name: 'Sun Pharma', weight: 18.0, color: '#c77dff' },
];

const fundamentals = [
  ['Revenue', '₹10.7T', '+7.1%', '+9.4%'],
  ['EBITDA margin', '17.6%', '+80bp', '+120bp'],
  ['Net debt / EBITDA', '1.34x', '-0.12x', '-0.28x'],
  ['Interest coverage', '5.8x', '+0.4x', '+1.1x'],
  ['FCFF', '₹684B', '+11.8%', '+22.5%'],
];

const funds = [
  ['HDFC Flexi Cap', 'Equity', '+18.6%', '+2,840', '1.12'],
  ['Parag Parikh Flexi Cap', 'Equity', '+17.9%', '+3,210', '0.94'],
  ['SBI Bluechip', 'Equity', '+13.4%', '+1,180', '1.08'],
  ['ICICI Pru Corp Bond', 'Debt', '+8.1%', '+640', '2.9y'],
  ['HDFC Short Term Debt', 'Debt', '+7.6%', '+420', '2.1y'],
];

function Sparkline({ values, positive }: { values: number[]; positive: boolean }) {
  const points = values
    .map((value, index) => `${(index / (values.length - 1)) * 82},${38 - value * 0.38}`)
    .join(' ');

  return (
    <svg className="sparkline" viewBox="0 0 82 40" aria-hidden="true">
      <polyline
        points={points}
        fill="none"
        stroke={positive ? '#35d49a' : '#ff5b5b'}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

function MainChart({ period }: { period: string }) {
  const series: Record<string, string> = {
    '1D': '0,110 50,104 95,118 140,85 190,91 240,60 290,67 340,39 390,54 440,26 500,33 560,17 620,24',
    '1M': '0,105 50,94 95,99 140,87 190,75 240,81 290,55 340,62 390,41 440,48 500,24 560,31 620,18',
    '1Y': '0,112 50,97 95,104 140,72 190,84 240,53 290,61 340,47 390,58 440,32 500,41 560,20 620,14',
    '5Y': '0,118 50,108 95,92 140,101 190,70 240,78 290,52 340,66 390,36 440,44 500,23 560,33 620,12',
  };
  const points = series[period] || series['1Y'];
  const fillPoints = `${points} 620,130 0,130`;

  return (
    <svg
      className="main-chart"
      viewBox="0 0 620 145"
      preserveAspectRatio="none"
      role="img"
      aria-label={`Nifty 50 ${period} illustrative price chart`}
    >
      <defs>
        <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ff9f1c" stopOpacity="0.28" />
          <stop offset="100%" stopColor="#ff9f1c" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[18, 45, 72, 99, 126].map((y) => (
        <line key={y} x1="0" y1={y} x2="620" y2={y} className="grid-line" />
      ))}
      <polygon points={fillPoints} fill="url(#chartFill)" />
      <polyline
        points={points}
        fill="none"
        stroke="#ff9f1c"
        strokeWidth="2.2"
        vectorEffect="non-scaling-stroke"
      />
      <line x1="0" y1="14" x2="620" y2="14" className="last-line" />
      <circle cx="620" cy="14" r="3.5" fill="#ff9f1c" />
    </svg>
  );
}

function Panel({
  title,
  code,
  action,
  children,
  className = '',
}: {
  title: string;
  code: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`terminal-panel ${className}`}>
      <header className="panel-header">
        <div>
          <span className="panel-code">{code}</span>
          <h2>{title}</h2>
        </div>
        {action}
      </header>
      {children}
    </section>
  );
}

function FinanceLab() {
  const [activeTab, setActiveTab] = useState<Tab>('OVERVIEW');
  const [period, setPeriod] = useState('1Y');
  const [selectedSymbol, setSelectedSymbol] = useState('NIFTY 50');
  const [searchOpen, setSearchOpen] = useState(false);
  const [watchlist, setWatchlist] = useState(marketRows);
  const [clock, setClock] = useState('');

  useEffect(() => {
    const updateClock = () =>
      setClock(
        new Intl.DateTimeFormat('en-GB', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
          timeZone: 'Asia/Kolkata',
        }).format(new Date()),
      );
    updateClock();
    const timer = window.setInterval(updateClock, 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setSearchOpen((open) => !open);
      }
      if (event.key === 'Escape') setSearchOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const activeReturn = useMemo(
    () => (activeTab === 'PORTFOLIO' ? '+2.7%' : '+0.84%'),
    [activeTab],
  );

  const removeWatch = (symbol: string) =>
    setWatchlist((rows) => rows.filter((row) => row.symbol !== symbol));

  return (
    <main className="finance-terminal">
      <div className="utility-bar">
        <div className="product-mark" aria-label="Meridian Finance Lab">
          <span className="mark-box">M</span>
          <span>MERIDIAN</span>
          <span className="product-suffix">FINANCE LAB</span>
        </div>
        <div className="market-status">
          <span className="status-dot" />
          NSE CLOSED
          <span className="divider">|</span>
          MUMBAI {clock} IST
        </div>
        <div className="utility-actions">
          <button type="button" onClick={() => setSearchOpen(true)}>
            SEARCH <kbd>⌘ K</kbd>
          </button>
          <button type="button">ALERTS <span className="notification">3</span></button>
          <span className="analyst">AK</span>
        </div>
      </div>

      <div className="command-bar">
        <div className="command-prompt">
          <span className="prompt-label">CMD</span>
          <span className="prompt-chevron">›</span>
          <span className="prompt-value">{selectedSymbol}</span>
          <span className="cursor-block" />
        </div>
        <nav aria-label="Finance sections">
          {(['OVERVIEW', 'EQUITIES', 'PORTFOLIO', 'MACRO / FX', 'FUNDS'] as Tab[]).map(
            (tab, index) => (
              <button
                type="button"
                key={tab}
                className={activeTab === tab ? 'active' : ''}
                onClick={() => setActiveTab(tab)}
              >
                <span>0{index + 1}</span> {tab}
              </button>
            ),
          )}
        </nav>
      </div>

      <div className="ticker-strip" aria-label="Market ticker">
        {[
          ['NIFTY 50', '26,118.20', '+0.84%'],
          ['SENSEX', '85,497.30', '+0.76%'],
          ['USD / INR', '83.712', '-0.12%'],
          ['BRENT', '$71.42', '+1.06%'],
          ['INDIA 10Y', '6.944%', '-3.1bp'],
          ['GOLD', '$2,674.10', '+0.31%'],
        ].map(([name, value, change]) => (
          <button type="button" key={name} onClick={() => setSelectedSymbol(name)}>
            <span>{name}</span>
            <b>{value}</b>
            <em className={change.startsWith('+') ? 'positive' : 'negative'}>{change}</em>
          </button>
        ))}
      </div>

      <div className="content-shell">
        <div className="page-intro">
          <div>
            <p className="eyebrow">FINANCE DATA LAB / INDIA</p>
            <h1>Cross-Asset Intelligence</h1>
            <p>Market, fundamental and portfolio analytics in one decision workspace.</p>
          </div>
          <div className="session-summary">
            <div><span>SESSION P&L</span><strong className="positive">+₹42,680</strong></div>
            <div><span>ACTIVE RETURN</span><strong>{activeReturn}</strong></div>
            <div><span>DATA AS OF</span><strong>26 SEP 2026</strong></div>
          </div>
        </div>

        <div className="dashboard-grid">
          <Panel
            title={`${selectedSymbol} · National Stock Exchange`}
            code="MKT 01"
            className="hero-chart-panel"
            action={
              <div className="period-switcher">
                {['1D', '1M', '1Y', '5Y'].map((item) => (
                  <button
                    type="button"
                    key={item}
                    className={period === item ? 'active' : ''}
                    onClick={() => setPeriod(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            }
          >
            <div className="quote-line">
              <strong>26,118.20</strong>
              <span className="positive">+217.45&nbsp;&nbsp;+0.84%</span>
              <span>52W 21,281.45 — 26,277.35</span>
            </div>
            <div className="chart-wrap">
              <MainChart period={period} />
              <div className="chart-axis"><span>OCT</span><span>JAN</span><span>APR</span><span>JUL</span><span>SEP</span></div>
            </div>
          </Panel>

          <Panel title="Market Pulse" code="MKT 02">
            <div className="pulse-grid">
              <div><span>ADV / DEC</span><strong>34 / 16</strong><small className="positive">68% breadth</small></div>
              <div><span>FII NET</span><strong>₹1,284Cr</strong><small className="positive">net buyer</small></div>
              <div><span>INDIA VIX</span><strong>12.84</strong><small className="negative">+2.1%</small></div>
              <div><span>PUT / CALL</span><strong>1.18x</strong><small>neutral</small></div>
            </div>
            <div className="sector-list">
              {[
                ['CAP GOODS', 2.34],
                ['ENERGY', 1.62],
                ['BANKS', 0.88],
                ['IT SERVICES', -0.41],
                ['HEALTHCARE', -0.72],
              ].map(([name, value]) => (
                <div key={String(name)}>
                  <span>{name}</span>
                  <div className="bar-track"><i style={{ width: `${Math.abs(Number(value)) * 32}%` }} className={Number(value) > 0 ? 'up' : 'down'} /></div>
                  <b className={Number(value) > 0 ? 'positive' : 'negative'}>{Number(value) > 0 ? '+' : ''}{value}%</b>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Five-Asset Watchlist" code="EQ 01" className="watchlist-panel">
            <div className="terminal-table watchlist-table">
              <div className="table-row table-head">
                <span>TICKER / COMPANY</span><span>LAST</span><span>DAY</span><span>VOL</span><span>TREND</span><span />
              </div>
              {watchlist.map((row) => (
                <button
                  type="button"
                  className="table-row data-row"
                  key={row.symbol}
                  onClick={() => setSelectedSymbol(row.symbol)}
                >
                  <span><b>{row.symbol}</b><small>{row.name}</small></span>
                  <span>{row.price}</span>
                  <span className={row.change > 0 ? 'positive' : 'negative'}>{row.change > 0 ? '+' : ''}{row.change.toFixed(2)}%</span>
                  <span>{row.volume}</span>
                  <span><Sparkline values={row.spark} positive={row.change > 0} /></span>
                  <span
                    className="remove-row"
                    role="button"
                    tabIndex={0}
                    title="Remove from watchlist"
                    onClick={(event) => {
                      event.stopPropagation();
                      removeWatch(row.symbol);
                    }}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') removeWatch(row.symbol);
                    }}
                  >
                    ×
                  </span>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Risk-Parity Portfolio" code="PF 01">
            <div className="portfolio-kpis">
              <div><span>ANN. RETURN</span><strong>16.8%</strong></div>
              <div><span>VOLATILITY</span><strong>11.2%</strong></div>
              <div><span>SHARPE</span><strong>1.08x</strong></div>
              <div><span>MAX DD</span><strong className="negative">-8.7%</strong></div>
            </div>
            <div className="allocation-bar">
              {allocation.map((asset) => (
                <i key={asset.name} style={{ width: `${asset.weight}%`, background: asset.color }} title={`${asset.name} ${asset.weight}%`} />
              ))}
            </div>
            <div className="allocation-legend">
              {allocation.map((asset) => (
                <span key={asset.name}><i style={{ background: asset.color }} />{asset.name}<b>{asset.weight}%</b></span>
              ))}
            </div>
          </Panel>

          <Panel title="Company Fundamentals" code="FA 01" className="fundamentals-panel">
            <div className="company-line">
              <div><span className="company-monogram">R</span><div><strong>Reliance Industries</strong><small>Oil-to-chemicals · Retail · Digital</small></div></div>
              <span className="rating">OVERWEIGHT</span>
            </div>
            <div className="terminal-table fundamentals-table">
              <div className="table-row table-head"><span>METRIC</span><span>FY26E</span><span>1Y Δ</span><span>3Y Δ</span></div>
              {fundamentals.map((row) => (
                <div className="table-row" key={row[0]}>
                  {row.map((cell, index) => <span className={index > 1 ? 'positive' : ''} key={cell}>{cell}</span>)}
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Commodity / FX Linkage" code="MX 01">
            <div className="relationship-header">
              <div><span>BRENT ↔ USD/INR</span><strong>ρ +0.42</strong><small>5Y daily returns</small></div>
              <div><span>INR-ADJ. BRENT</span><strong>+8.7%</strong><small>12M total return</small></div>
            </div>
            <div className="regression-strip">
              <span>Δ USDINR<sub>t</sub> =</span>
              <b>0.08</b>
              <span>+</span>
              <b>0.14 × BRENT<sub>t−1</sub></b>
              <em>R² 0.18 · p 0.03</em>
            </div>
            <p className="insight"><span>READ</span> Higher crude prices precede modest INR weakness; the relationship strengthens during oil-supply shocks.</p>
          </Panel>

          <Panel title="Flow Monitor" code="MF 01" className="fund-panel">
            <div className="terminal-table funds-table">
              <div className="table-row table-head"><span>FUND</span><span>CLASS</span><span>12M RET.</span><span>NET FLOW ₹CR</span><span>RISK</span></div>
              {funds.map((row) => (
                <div className="table-row" key={row[0]}>
                  {row.map((cell, index) => <span className={index === 2 || index === 3 ? 'positive' : ''} key={cell}>{cell}</span>)}
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="News & Catalysts" code="NW 01" className="news-panel">
            <div className="news-list">
              {news.map((item) => (
                <article key={item.time}>
                  <time>{item.time}</time><span>{item.tag}</span><p>{item.headline}</p>
                </article>
              ))}
            </div>
          </Panel>
        </div>

        <footer className="terminal-footer">
          <span><b>ILLUSTRATIVE DATA</b> · For academic demonstration only. Not investment advice or a live data feed.</span>
          <span>SOURCES TO REPLACE: BLOOMBERG · PROWESSDX · ACE MF</span>
        </footer>
      </div>

      {searchOpen && (
        <div className="search-overlay" role="dialog" aria-modal="true" aria-label="Search securities">
          <button className="overlay-backdrop" type="button" aria-label="Close search" onClick={() => setSearchOpen(false)} />
          <div className="search-dialog">
            <div className="search-input">
              <span>SEARCH</span>
              <input autoFocus placeholder="Enter ticker, company, function or keyword…" />
              <kbd>ESC</kbd>
            </div>
            <p>RECENT SECURITIES</p>
            {marketRows.slice(0, 4).map((row) => (
              <button
                type="button"
                key={row.symbol}
                onClick={() => {
                  setSelectedSymbol(row.symbol);
                  setSearchOpen(false);
                }}
              >
                <b>{row.symbol}</b><span>{row.name}</span><em>{row.price}</em>
              </button>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}

export default FinanceLab;
