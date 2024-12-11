$.ajaxSetup({
    headers: { 'X-CSRFToken': csrf_token },
    type: 'POST',
});

$(document).ready(function () {
    // 設置點擊事件
    $("#function-tabs .nav-link").click(function () {
        // 獲取當前點擊的按鈕的 target (對應的功能區塊)
        const target = $(this).data("target");

        // 1. 移除所有按鈕的 active 樣式
        $("#function-tabs .nav-link").removeClass("active");

        // 2. 隱藏所有的功能區塊
        $(".tab-content").addClass("d-none");

        // 3. 為當前點擊的按鈕加上 active 樣式
        $(this).addClass("active");

        // 4. 顯示對應的功能區塊
        $(target).removeClass("d-none");

        if (target === "#distance-method") {
            loadDistanceMethod();
        } else if (target === "#other-method") {
            loadOtherMethod();
        } else if (target === "#backtrader") {
            loadBacktrader();
        }
    });

    // 預設載入 Distance Method
    // loadDistanceMethod();
    
});
function loadOtherMethod() {
    $("#submit2").on("click", function (e) {
        e.preventDefault(); // 防止表單提交的默認行為
        
        $.ajax({
            url: 'rsi_cross_ajax/', // API 的 URL
            data: {
                'stock': document.getElementById('stock1').value,
                'short_rsi': document.getElementById('short_rsi').value,
                'long_rsi': document.getElementById('long_rsi').value,
                'start_date': document.getElementById('start_date').value,
                'end_date': document.getElementById('end_date').value
            },
    
            success: function (response) {
                // 渲染 Datatable
                renderDatatable(response.trade_results);
                // 渲染報酬率和最大回撤圖表
                renderProfitDrawdownChart(response.profit_mdd_data);
                // 渲染新的OHLC圖表
                renderNewChart(response.buy_dates, response.sell_dates, response.ohlc, response.volume); // 呼叫這個新函數
                // 顯示績效數據
                renderPerformanceMetrics(response.performance_data);            
            },
            error: function (error) {
                console.error('Error fetching RSI cross trade data:', error);
            }
        });
    });
}

function loadBacktrader(){
    $('#submit3').on('click', function (e) {
        e.preventDefault();  // 防止表單的默認提交

        $.ajax({
            url: 'run_strategy/',  // URL對應你的views.py中的路徑
            type: 'POST',
            data: {
                stock1: $('#stock1').val(),  // 股票代號
                order_units: $('#order_units').val(),  // 單筆下單股數
                exit_strategy: $('#exit_strategy').val(),  // 出場策略
                strategy: $('#strategy').val(),  // 進場策略
                short_rsi: $('#short_rsi').val(),  // 短期RSI週期
                long_rsi: $('#long_rsi').val(),  // 長期RSI週期
                capital: $('#capital').val(),  // 初始資金
                fee: $('#fee').val(),  // 手續費
                start_date: $('#start_date').val(),  // 開始日期
                end_date: $('#end_date').val()  // 結束日期
            },
            success: function (response) {
                // 清除現有的表格數據
                $('#performance-table').empty();

                // 顯示資產變化
                let assetHtml = `
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr style="background-color: #f2f2f2; font-weight: bold; font-size: 20px;">
                            <th colspan="2">資產變化</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>期初資產</td><td>${response.initial_cash}</td></tr>
                            <tr><td>期末資產</td><td>${response.final_cash.toFixed(0)}</td></tr>
                        </tbody>
                    </table>
                `;

                // 顯示策略績效
                let performanceHtml = `
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr style="background-color: #f2f2f2; font-weight: bold; font-size: 20px;">
                            <th colspan="2">策略績效</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>SharpeRatio</td><td>${response.sharpe_ratio}</td></tr>
                            <tr><td>MaxDrawdown</td><td>${response.max_drawdown}</td></tr>
                        </tbody>
                    </table>
                `;

                // 顯示年度報酬率
                let annualReturnHtml = `
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr style="background-color: #f2f2f2; font-weight: bold; font-size: 20px;">
                            <th colspan="2">年度報酬率</th></tr>
                        </thead>
                        <thead>
                            <tr><th>Year</th><th>Annual Return(%)</th></tr>
                        </thead>
                        <tbody>
                `;
                $.each(response.annual_return, function (year, returnValue) {
                    annualReturnHtml += `<tr><td>${year}</td><td>${(returnValue).toFixed(3)}</td></tr>`;
                });
                annualReturnHtml += '</tbody></table>';

                // 將結果附加到表格中
                $('#performance-table').append(assetHtml + performanceHtml + annualReturnHtml);
                
                // 顯示交易紀錄的標題
                let transactionHead = `
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr style="background-color: #f2f2f2; font-weight: bold; font-size: 20px;">
                            <th colspan="4">交易紀錄</th></tr>
                        </thead>
                    </table>
                `;
               
                // 將交易紀錄的表頭添加到 DOM
                $('#performance-table').append(transactionHead);

                // 使用 DataTable 顯示交易紀錄
                $('#transactions-table').DataTable({
                    data: response.transactions,
                    destroy: true, // 允許在多次更新中重新初始化表格
                    columns: [
                        { title: "Date", data: 'date' },
                        { title: "Amount", data: 'amount' },
                        { title: "Price", data: 'price' },
                        { title: "Value", data: 'value' }
                    ],
                    pageLength: 10, // 每頁顯示 10 筆
                    lengthMenu: [5, 10, 20, 50], // 可以選擇每頁顯示筆數
                    searching: false,
                    ordering: true // 啟用排序功能
                });
            },
            error: function (error) {
                console.error('Error fetching strategy result:', error);
            }
        });
    });
}