<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CryptoGamma Pro</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #03050a; --bg-card: #090e18; --border-color: #151d2a;
            --neon-glow: rgba(0, 122, 255, 0.2); --text-main: #ffffff; --text-muted: #8b9bb4;
            --accent-blue: #007aff; --accent-green: #0ecb81; --accent-red: #f6465d;
        }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body {
            background-color: var(--bg-main); color: var(--text-main);
            font-family: 'Inter', sans-serif; margin: 0; padding: 0; height: 100vh;
            display: flex; flex-direction: column; overflow: hidden;
            background-image: radial-gradient(circle at 50% -20%, #0a1628 0%, var(--bg-main) 70%);
        }
        .app-container { flex: 1; display: flex; flex-direction: column; max-width: 500px; margin: 0 auto; width: 100%; overflow: hidden; }
        .content { flex: 1; overflow-y: auto; padding: 20px; padding-bottom: 100px; }
        .content::-webkit-scrollbar { display: none; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .header-logo { display: flex; align-items: center; gap: 12px; }
        
        /* 3D Ракета */
        .logo-icon { 
            width: 38px; height: 38px; 
            background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/rocket-3d-icon-download-in-png-blend-fbx-gltf-file-formats--spaceship-launch-startup-business-pack-icons-5355781.png');
            background-size: contain; background-repeat: no-repeat; background-position: center;
            filter: drop-shadow(0 0 10px rgba(0, 122, 255, 0.4)); 
        }
        .header-title h1 { margin: 0; font-size: 19px; font-family: 'Montserrat', sans-serif; font-weight: 800; letter-spacing: 0.5px; text-shadow: 0 0 15px rgba(255, 255, 255, 0.15); }
        .header-title p { margin: 2px 0 0; font-size: 11px; color: var(--text-muted); font-weight: 500; }
        .user-id { background: var(--bg-card); padding: 6px 12px; border-radius: 20px; border: 1px solid var(--border-color); font-size: 11px; color: var(--text-muted); font-weight: 500; box-shadow: 0 0 10px rgba(0,0,0,0.5) inset; }

        .btn-back { background: none; border: none; color: var(--text-main); font-size: 16px; cursor: pointer; margin-bottom: 15px; display: flex; align-items: center; gap: 5px; font-weight: 600; padding: 0; }

        .balance-card { background: linear-gradient(145deg, #0d121c, #080b12); border-radius: 22px; padding: 24px; border: 1px solid var(--border-color); margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4), 0 0 20px var(--neon-glow); }
        .balance-info { display: flex; flex-direction: column; gap: 4px; }
        .balance-label { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
        .balance-amount { font-size: 34px; font-family: 'Montserrat', sans-serif; font-weight: 800; color: #fff; display: flex; align-items: baseline; gap: 6px; text-shadow: 0 0 20px rgba(255, 255, 255, 0.3); }
        .balance-amount span { font-size: 14px; color: var(--accent-blue); font-family: 'Inter', sans-serif; font-weight: 600; text-shadow: none; }
        
        .action-bar { display: flex; gap: 12px; margin-bottom: 24px; }
        .btn-action { flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; display: flex; align-items: center; justify-content: center; gap: 10px; cursor: pointer; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); font-size: 14px; font-weight: 600; color: #fff; }
        .btn-action:active { transform: scale(0.95); }
        .btn-primary { background: var(--accent-blue); border-color: var(--accent-blue); box-shadow: 0 5px 20px rgba(0, 122, 255, 0.4); }
        .btn-primary:active { background: #0066d6; box-shadow: 0 2px 10px rgba(0, 122, 255, 0.6); }

        .chart-card { background: var(--bg-card); border-radius: 22px; padding: 20px; border: 1px solid var(--border-color); margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .coin-title { display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 16px; }
        .coin-price-real { font-size: 32px; font-family: 'Montserrat', sans-serif; font-weight: 800; text-shadow: 0 0 20px rgba(255,255,255,0.15); }
        .coin-change-real { font-size: 14px; font-weight: 600; padding: 4px 8px; border-radius: 8px; background: rgba(255,255,255,0.05); }
        .chart-container { height: 200px; width: 100%; position: relative; margin-top: 10px; }
        .chart-large { height: 250px; }

        .timeframes { display: flex; gap: 8px; margin-top: 15px; justify-content: space-between; }
        .tf-btn { flex: 1; background: rgba(255,255,255,0.04); border: 1px solid transparent; color: var(--text-muted); padding: 10px 0; border-radius: 10px; font-size: 12px; font-weight: 600; cursor: pointer; text-align: center; transition: 0.2s; }
        .tf-btn.active { background: var(--accent-blue); color: #fff; box-shadow: 0 0 15px rgba(0, 122, 255, 0.4); border-color: var(--accent-blue); }

        .coin-list { background: var(--bg-card); border-radius: 22px; border: 1px solid var(--border-color); padding: 10px 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .coin-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid var(--border-color); cursor: pointer; transition: 0.2s; }
        .coin-row:active { opacity: 0.7; }
        .coin-row:last-child { border-bottom: none; }
        .coin-row-info { display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 15px; }
        
        .coin-icon-img { width: 28px; height: 28px; background-size: contain; background-repeat: no-repeat; background-position: center; filter: drop-shadow(0 0 6px rgba(0,0,0,0.4)); }
        .icon-btc { background-image: url('https://assets.coingecko.com/coins/images/1/small/bitcoin.png'); }
        .icon-eth { background-image: url('https://assets.coingecko.com/coins/images/279/small/ethereum.png'); }
        .icon-sol { background-image: url('https://assets.coingecko.com/coins/images/4128/small/solana.png'); }
        .icon-bnb { background-image: url('https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png'); }

        .coin-row-price { text-align: right; font-weight: 600; font-size: 15px; }
        .green { color: var(--accent-green); text-shadow: 0 0 10px rgba(14, 203, 129, 0.3); }
        .red { color: var(--accent-red); text-shadow: 0 0 10px rgba(246, 70, 93, 0.3); }

        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; }
        .stat-box { background: rgba(255,255,255,0.02); padding: 16px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.05); }
        .stat-label { font-size: 11px; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; font-weight: 600; }
        .stat-value { font-size: 16px; font-weight: 600; color: #fff; }

        .bottom-nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 500px; background: rgba(3, 5, 10, 0.9); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-around; padding: 12px 0 16px 0; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: var(--text-muted); font-size: 10px; font-weight: 600; cursor: pointer; transition: 0.3s; gap: 4px; }
        .nav-item.active { color: var(--accent-blue); }
        
        .nav-icon-img { width: 24px; height: 24px; background-size: contain; background-repeat: no-repeat; background-position: center; filter: grayscale(100%) opacity(0.5); transition: 0.3s; }
        .nav-item.active .nav-icon-img { filter: grayscale(0%) opacity(1) drop-shadow(0 0 8px var(--accent-blue)); transform: scale(1.1); }

        .icon-home { background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/home-3d-icon-download-in-png-blend-fbx-gltf-file-formats--house-building-estate-pack-icons-4639111.png'); }
        .icon-market { background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/finance-3d-icon-download-in-png-blend-fbx-gltf-file-formats--chart-graph-market-growth-pack-icons-4639093.png'); }
        .icon-history { background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/time-is-money-3d-icon-download-in-png-blend-fbx-gltf-file-formats--clock-history-watch-pack-icons-4639105.png'); }
        .icon-ref { background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/group-3d-icon-download-in-png-blend-fbx-gltf-file-formats--people-users-team-friends-pack-icons-4639138.png'); }
        .icon-admin { background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/user-3d-icon-download-in-png-blend-fbx-gltf-file-formats--profile-avatar-person-pack-icons-4639112.png'); }

        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .admin-input { width: 100%; padding: 16px; margin-bottom: 12px; background: rgba(0,0,0,0.4); border: 1px solid var(--border-color); color: #fff; border-radius: 12px; box-sizing: border-box; outline: none; font-size: 14px; transition: 0.2s; }
        .admin-input:focus { border-color: var(--accent-blue); box-shadow: 0 0 15px var(--neon-glow); }

        .invoice-card { background: var(--bg-card); border-radius: 22px; padding: 30px 20px; border: 1px solid var(--border-color); text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
        .invoice-address { background: rgba(0,0,0,0.5); padding: 18px; border-radius: 14px; border: 1px dashed var(--accent-blue); font-family: monospace; font-size: 15px; margin: 20px 0; word-break: break-all; color: var(--accent-blue); font-weight: 600; }
        
        .qr-placeholder { width: 110px; height: 110px; margin: 0 auto 20px; background-image: url('https://cdn3d.iconscout.com/3d/premium/thumb/dollar-coin-3d-icon-download-in-png-blend-fbx-gltf-file-formats--money-currency-finance-pack-icons-5087056.png'); background-size: contain; background-repeat: no-repeat; background-position: center; filter: drop-shadow(0 0 25px rgba(0, 243, 255, 0.4)); }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="content">
            <!-- ГЛАВНАЯ -->
            <div id="tab-home" class="tab-content active">
                <div class="header">
                    <div class="header-logo">
                        <div class="logo-icon"></div>
                        <div class="header-title"><h1>CRYPTOGAMMA</h1><p>Pro Trading Wallet</p></div>
                    </div>
                    <div class="user-id" id="user-id">ID: ...</div>
                </div>

                <div class="balance-card">
                    <div class="balance-info">
                        <div class="balance-label">Ваш баланс</div>
                        <div class="balance-amount" id="balance-display">0.00 <span>USDT</span></div>
                    </div>
                </div>

                <div class="action-bar">
                    <button class="btn-action btn-primary" onclick="switchTab('invoice')">
                        <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 5v14m-7-7l7 7 7-7"/></svg> Пополнить
                    </button>
                    <button class="btn-action" onclick="sendAction('withdraw')">
                        <svg width="24" height="24" fill="none" stroke="#fff" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a1 1 0 01-1 1h-3v2h2a1 1 0 010 2h-2v1a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2h12a2 2 0 012 2v1h2a1 1 0 011 1v4zM17 7H5v10h12V7zm2 5h-2v2h2v-2z"/></svg> Вывести
                    </button>
                </div>

                <div class="chart-card">
                    <div class="chart-header">
                        <div class="coin-title"><div class="coin-icon-img icon-btc"></div> BTC/USDT</div>
                        <div class="coin-change-real" id="btc-change">+0.00%</div>
                    </div>
                    <div class="coin-price-real" id="btc-price">$0.00</div>
                    <div class="chart-container"><canvas id="btcChart"></canvas></div>
                </div>

                <div class="coin-list">
                    <div class="coin-row" onclick="openCoinDetail('ethereum', 'Ethereum', 'ETH')">
                        <div class="coin-row-info"><div class="coin-icon-img icon-eth"></div> Ethereum (ETH)</div>
                        <div class="coin-row-price" id="eth-price">$0.00</div>
                    </div>
                    <div class="coin-row" onclick="openCoinDetail('solana', 'Solana', 'SOL')">
                        <div class="coin-row-info"><div class="coin-icon-img icon-sol"></div> Solana (SOL)</div>
                        <div class="coin-row-price" id="sol-price">$0.00</div>
                    </div>
                    <div class="coin-row" onclick="openCoinDetail('binancecoin', 'BNB', 'BNB')">
                        <div class="coin-row-info"><div class="coin-icon-img icon-bnb"></div> BNB</div>
                        <div class="coin-row-price" id="bnb-price">$0.00</div>
                    </div>
                </div>
            </div>

            <!-- СОЗДАТЬ СЧЁТ -->
            <div id="tab-invoice" class="tab-content">
                <button class="btn-back" onclick="switchTab('home')">← Назад</button>
                <div class="invoice-card">
                    <h2 style="margin-top: 0; font-size: 22px; font-family: 'Montserrat';">Пополнение баланса</h2>
                    <p style="color: var(--text-muted); font-size: 14px; line-height: 1.4;">Создай персональный адрес для перевода USDT (TRC-20) с других кошельков.</p>
                    <div class="qr-placeholder"></div>
                    <div class="invoice-address" id="invoice-address">Нажми кнопку ниже, чтобы сгенерировать адрес...</div>
                    <button class="btn-action btn-primary" style="width: 100%; justify-content: center; padding: 18px; font-size: 15px;" onclick="sendAction('create_invoice')">Сгенерировать адрес</button>
                </div>
            </div>

            <!-- ДЕТАЛИ МОНЕТЫ -->
            <div id="tab-detail" class="tab-content">
                <button class="btn-back" onclick="switchTab('home')">← Назад</button>
                <div class="chart-card" style="margin-top: 0;">
                    <div class="chart-header">
                        <div class="coin-title" id="detail-title">Ethereum</div>
                        <div class="coin-change-real" id="detail-change">+0.00%</div>
                    </div>
                    <div class="coin-price-real" id="detail-price">$0.00</div>
                    <div class="chart-container chart-large"><canvas id="detailChart"></canvas></div>
                    <div class="timeframes" id="timeframes">
                        <div class="tf-btn" onclick="setTimeframe('1', this)">1Ч</div>
                        <div class="tf-btn active" onclick="setTimeframe('24', this)">24Ч</div>
                        <div class="tf-btn" onclick="setTimeframe('168', this)">7Д</div>
                        <div class="tf-btn" onclick="setTimeframe('720', this)">1М</div>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-box"><div class="stat-label">Максимум (24ч)</div><div class="stat-value" id="detail-high">$0</div></div>
                        <div class="stat-box"><div class="stat-label">Минимум (24ч)</div><div class="stat-value" id="detail-low">$0</div></div>
                        <div class="stat-box"><div class="stat-label">Объем (24ч)</div><div class="stat-value" id="detail-vol">$0</div></div>
                        <div class="stat-box"><div class="stat-label">Сделок</div><div class="stat-value" id="detail-count">0</div></div>
                    </div>
                </div>
            </div>

            <!-- РЫНОК -->
            <div id="tab-market" class="tab-content">
                <div class="header"><div class="header-title"><h1>📊 Рынок</h1></div></div>
                <div class="coin-list">
                    <div class="coin-row" onclick="openCoinDetail('bitcoin', 'Bitcoin', 'BTC')"><div class="coin-row-info"><div class="coin-icon-img icon-btc"></div> Bitcoin</div><div class="coin-row-price" id="m-btc">$0</div></div>
                    <div class="coin-row" onclick="openCoinDetail('ethereum', 'Ethereum', 'ETH')"><div class="coin-row-info"><div class="coin-icon-img icon-eth"></div> Ethereum</div><div class="coin-row-price" id="m-eth">$0</div></div>
                    <div class="coin-row" onclick="openCoinDetail('solana', 'Solana', 'SOL')"><div class="coin-row-info"><div class="coin-icon-img icon-sol"></div> Solana</div><div class="coin-row-price" id="m-sol">$0</div></div>
                </div>
            </div>

            <!-- ИСТОРИЯ (НОВАЯ) -->
            <div id="tab-history" class="tab-content">
                <div class="header"><div class="header-title"><h1>📜 История</h1></div></div>
                <div class="coin-list">
                    <button class="btn-action btn-primary" style="width: 100%; justify-content: center;" onclick="sendAction('get_history')">Загрузить историю</button>
                </div>
            </div>

            <!-- РЕФЕРАЛКА (НОВАЯ) -->
            <div id="tab-ref" class="tab-content">
                <div class="header"><div class="header-title"><h1>👥 Рефералка</h1></div></div>
                <div class="chart-card" style="text-align: center;">
                    <p style="color: var(--text-muted); font-size: 14px;">Приглашай друзей и получай 0.05 USDT за каждого!</p>
                    <button class="btn-action btn-primary" style="width: 100%; justify-content: center; margin-top: 15px;" onclick="sendAction('ref_link')">Пригласить друга</button>
                </div>
            </div>

            <!-- АДМИНКА (ПОЛНАЯ) -->
            <div id="tab-admin" class="tab-content">
                <div class="header"><div class="header-title"><h1>👑 Админка</h1></div></div>
                <div class="chart-card">
                    <h3 style="margin-top: 0;">Начислить баланс</h3>
                    <input type="number" id="admin-user-id" class="admin-input" placeholder="ID пользователя">
                    <input type="number" id="admin-amount" class="admin-input" placeholder="Сумма">
                    <button class="btn-action btn-primary" style="width: 100%; justify-content: center;" onclick="adminAction('add_balance')">НАЧИСЛИТЬ</button>
                </div>
                <div class="chart-card">
                    <h3 style="margin-top: 0;">Забанить / Разбанить</h3>
                    <input type="number" id="admin-ban-id" class="admin-input" placeholder="ID пользователя">
                    <button class="btn-action" style="width: 100%; justify-content: center; background: rgba(246, 70, 93, 0.2); color: #f6465d; border-color: #f6465d;" onclick="adminAction('toggle_ban')">ИЗМЕНИТЬ СТАТУС</button>
                </div>
                <div class="chart-card">
                    <h3 style="margin-top: 0;">Рассылка</h3>
                    <input type="text" id="admin-broadcast" class="admin-input" placeholder="Текст...">
                    <button class="btn-action" style="width: 100%; justify-content: center;" onclick="adminAction('broadcast')">ОТПРАВИТЬ</button>
                </div>
            </div>
        </div>

        <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('home')" id="nav-home"><div class="nav-icon-img icon-home"></div><span>Главная</span></div>
            <div class="nav-item" onclick="switchTab('market')" id="nav-market"><div class="nav-icon-img icon-market"></div><span>Рынок</span></div>
            <div class="nav-item" onclick="switchTab('history')" id="nav-history"><div class="nav-icon-img icon-history"></div><span>История</span></div>
            <div class="nav-item" onclick="switchTab('ref')" id="nav-ref"><div class="nav-icon-img icon-ref"></div><span>Рефералка</span></div>
            <div class="nav-item" onclick="switchTab('admin')" id="nav-admin" style="display: none;"><div class="nav-icon-img icon-admin"></div><span>Профиль</span></div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand(); tg.ready(); tg.setHeaderColor('#03050a'); tg.setBackgroundColor('#03050a');
        
        let userId = tg.initDataUnsafe?.user?.id;
        if (userId) {
            document.getElementById('user-id').innerText = `ID: ${userId}`;
            if ([8636027393].includes(userId)) document.getElementById('nav-admin').style.display = 'flex';
        }

        let mainChart = null; let detailChart = null; let currentSymbol = 'ethereum'; let currentTimeframe = '24';
        Chart.defaults.color = '#8b9bb4'; Chart.defaults.font.family = 'Inter';

        async function fetchChartData(symbol, timeframe) {
            try {
                const res = await fetch(`https://api.coingecko.com/api/v3/coins/${symbol}/market_chart?vs_currency=usd&days=${timeframe}`);
                const data = await res.json();
                const prices = data.prices.map(item => item[1]);
                const labels = data.prices.map(item => {
                    let date = new Date(item[0]);
                    if(timeframe === '1' || timeframe === '24') return date.getHours() + ':' + ('0'+date.getMinutes()).slice(-2);
                    return date.getDate() + '.' + (date.getMonth()+1);
                });
                return { prices, labels };
            } catch (e) { return { prices: [], labels: [] }; }
        }

        async function updateMainChart() {
            const { prices, labels } = await fetchChartData('bitcoin', '24');
            if (prices.length === 0) return;
            if (mainChart) mainChart.destroy();
            const ctx = document.getElementById('btcChart').getContext('2d');
            let gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, 'rgba(14, 203, 129, 0.3)'); gradient.addColorStop(1, 'rgba(14, 203, 129, 0)');
            mainChart = new Chart(ctx, {
                type: 'line', data: { labels: labels, datasets: [{ data: prices, borderColor: '#0ecb81', borderWidth: 2, backgroundColor: gradient, fill: true, pointRadius: 0, tension: 0.1 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
            });
        }

        async function openCoinDetail(symbol, name, iconHTML) {
            currentSymbol = symbol;
            document.getElementById('detail-title').innerHTML = `<div class="coin-icon-img icon-${symbol}"></div> ${name}/USDT`;
            switchTab('detail');
            document.querySelectorAll('.tf-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tf-btn')[1].classList.add('active');
            currentTimeframe = '24';
            loadDetailChart();
            fetchStats(symbol);
        }

        async function loadDetailChart() {
            const { prices, labels } = await fetchChartData(currentSymbol, currentTimeframe);
            if (prices.length === 0) return;
            if (detailChart) detailChart.destroy();
            const ctx = document.getElementById('detailChart').getContext('2d');
            let gradient = ctx.createLinearGradient(0, 0, 0, 250);
            gradient.addColorStop(0, 'rgba(0, 122, 255, 0.3)'); gradient.addColorStop(1, 'rgba(0, 122, 255, 0)');
            detailChart = new Chart(ctx, {
                type: 'line', data: { labels: labels, datasets: [{ data: prices, borderColor: '#007aff', borderWidth: 2, backgroundColor: gradient, fill: true, pointRadius: 0, tension: 0.1 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } }, interaction: { mode: 'index', intersect: false } }
            });
        }

        function setTimeframe(tf, btn) {
            currentTimeframe = tf;
            document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadDetailChart();
        }

        async function fetchStats(symbol) {
            try {
                const res = await fetch(`https://api.coingecko.com/api/v3/coins/${symbol}`);
                const data = await res.json();
                let price = data.market_data.current_price.usd; 
                let change = data.market_data.price_change_percentage_24h;
                let colorClass = change >= 0 ? 'green' : 'red'; let arrow = change >= 0 ? '▲' : '▼';
                document.getElementById('detail-price').innerText = `$${price > 1000 ? price.toLocaleString('en-US', {minimumFractionDigits: 2}) : price.toFixed(2)}`;
                document.getElementById('detail-change').innerText = `${arrow} ${Math.abs(change).toFixed(2)}%`;
                document.getElementById('detail-change').className = `coin-change-real ${colorClass}`;
                document.getElementById('detail-high').innerText = `$${data.market_data.high_24h.usd.toLocaleString()}`;
                document.getElementById('detail-low').innerText = `$${data.market_data.low_24h.usd.toLocaleString()}`;
                document.getElementById('detail-vol').innerText = `$${(data.market_data.total_volume.usd / 1000000).toFixed(1)}M`;
                document.getElementById('detail-count').innerText = "---";
            } catch (e) {}
        }

        async function fetchPrices() {
            try {
                const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin&vs_currencies=usd&include_24hr_change=true');
                const data = await res.json();
                
                const updateRow = (id, priceId, changeId, mPriceId) => {
                    if(!data[id]) return;
                    let price = data[id].usd; let change = data[id].usd_24h_change || 0;
                    let formatPrice = price > 1000 ? price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : price.toFixed(2);
                    let colorClass = change >= 0 ? 'green' : 'red'; let arrow = change >= 0 ? '▲' : '▼'; let changeStr = `${arrow} ${Math.abs(change).toFixed(2)}%`;
                    
                    if(priceId) { let el = document.getElementById(priceId); if(el) { el.innerText = `$${formatPrice}`; el.className = `coin-price-real ${colorClass}`; } }
                    if(changeId) { let el = document.getElementById(changeId); if(el) { el.innerText = changeStr; el.className = `coin-change-real ${colorClass}`; } }
                    if(mPriceId) { let el = document.getElementById(mPriceId); if(el) { el.innerText = `$${formatPrice}`; el.className = `coin-row-price ${colorClass}`; } }
                };

                updateRow('bitcoin', 'btc-price', 'btc-change', 'm-btc');
                updateRow('ethereum', 'eth-price', null, 'm-eth');
                updateRow('solana', 'sol-price', null, 'm-sol');
                updateRow('binancecoin', 'bnb-price', null, null);
            } catch (e) {}
        }

        updateMainChart(); fetchPrices();
        setInterval(() => {
            fetchPrices();
            if(document.getElementById('tab-detail').classList.contains('active')) { fetchStats(currentSymbol); } 
            else { updateMainChart(); }
        }, 15000);

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById(`tab-${tabName}`).classList.add('active');
            if(tabName !== 'detail' && tabName !== 'invoice') {
                let navId = tabName === 'home' ? 'nav-home' : (tabName === 'history' ? 'nav-history' : (tabName === 'market' ? 'nav-market' : (tabName === 'ref' ? 'nav-ref' : 'nav-admin')));
                if (document.getElementById(navId)) document.getElementById(navId).classList.add('active');
            } else {
                document.getElementById('nav-market').classList.add('active');
            }
        }

        function sendAction(action) { tg.sendData(JSON.stringify({ action: action })); tg.close(); }
        
        function adminAction(action) {
            if (action === 'add_balance') { 
                let t = document.getElementById('admin-user-id').value; let a = document.getElementById('admin-amount').value; 
                if (!t || !a) return alert("Заполни поля!"); 
                tg.sendData(JSON.stringify({ action: "add_balance", target_id: t, amount: a })); 
                tg.close(); 
            } else if (action === 'toggle_ban') {
                let t = document.getElementById('admin-ban-id').value; 
                if (!t) return alert("Введи ID!"); 
                tg.sendData(JSON.stringify({ action: "toggle_ban", target_id: t })); 
                tg.close(); 
            } else if (action === 'broadcast') {
                let txt = document.getElementById('admin-broadcast').value; 
                if (!txt) return alert("Введи текст!"); 
                tg.sendData(JSON.stringify({ action: "broadcast", text: txt })); 
                tg.close(); 
            }
        }
    </script>
</body>
</html>
