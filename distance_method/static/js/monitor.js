function remove_from_track_list(track_row){

    var track_spread = new FormData;
    track_spread.append("stock1", track_row['stock1']);
    track_spread.append("stock2", track_row['stock2']);
    track_spread.append("start_date", track_row['start_date']);
    track_spread.append("end_date", track_row['end_date']);
    track_spread.append("method", track_row['method']);
    track_spread.append("window_size", track_row['window_size']);
    track_spread.append("n_times", track_row['n_times']);
    track_spread.append("stop_loss_percentage", track_row['stop_loss_percentage']);
    track_spread.append("max_recover_days", track_row['max_recover_days']);
    track_spread.append("consider_optimization", track_row['consider_optimization']);
    track_spread.append("critical_value", track_row['critical_value']);
    track_spread.append("consider_p_value", track_row['consider_p_value']);
    track_spread.append("track_date", track_row['track_date']);

    $.ajax({
      url: "/monitor/remove_track/",
      data:track_spread, 
      type:'POST',
      dataType: 'json',
      processData:false,
      contentType:false,
      success:function(data)
      {
        alert("Remove successfully!");
      }
    });
}

function run_monitor_analysis(track_row){
    var track_spread = new FormData;
    track_spread.append("stock1", track_row['stock1']);
    track_spread.append("stock2", track_row['stock2']);
    track_spread.append("start_date", track_row['start_date']);
    track_spread.append("end_date", track_row['end_date']);
    track_spread.append("method", track_row['method']);
    track_spread.append("window_size", track_row['window_size']);
    track_spread.append("n_times", track_row['n_times']);
    track_spread.append("stop_loss_percentage", track_row['stop_loss_percentage']);
    track_spread.append("max_recover_days", track_row['max_recover_days']);
    track_spread.append("consider_optimization", track_row['consider_optimization']);
    track_spread.append("critical_value", track_row['critical_value']);
    track_spread.append("consider_p_value", track_row['consider_p_value']);
    track_spread.append("track_date", track_row['track_date']);

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/monitor/run_tracker/",
        data: track_spread,
        processData: false,
        contentType: false,
        success: function (response) {
            $('#staticBackdrop').modal('show');
            
            var indexCell = $(`#target_button`);
            if (indexCell.length) {
                indexCell.html(`<button type="button" class="btn btn-success">Results</button>`);
                indexCell.removeAttr('id'); // 刪除 id
            } 

            var stockData = response.stock_data;
            var signalsData = response.signals_data;
            var spreadData = response.spread_data;
            var upperLineData = response.upper_line_data;
            var lowerLineData = response.lower_line_data;
            var middleLineData = response.middle_line_data;
            var profitLossData = response.profit_loss.daily_value;
            var cashData = response.profit_loss.cash_value;
            var EntryPoint = response.profit_loss.entry_point;  // 進場點
            var ExitPoint = response.profit_loss.exit_point;    // 出場點
            var stock1 = $("#stock1").val();
            var stock2 = $("#stock2").val();

            // 在Highcharts中顯示股票價格和交易信號
            renderHighchart(stockData, signalsData);
            renderSpreadChart(spreadData, upperLineData, lowerLineData, middleLineData, signalsData);
            renderProfitLossChart(profitLossData, cashData, EntryPoint, ExitPoint);
            // 在Datatable中顯示交易信號
            renderDatatable(signalsData, stock1, stock2);
            renderDatatable2(response.profit_loss.trade_results, stock1, stock2);
       },
    });
}

$(document).ready(function (){
    $.ajax({
        url: "/monitor/get_track_list/",
        type: "post",
        dataType : 'json',
        processData : false,
        contentType : false,
        success: function (response) {

            var table = $("#monitor").DataTable({
                data: response.track_data,
                "createdRow": function (row, data, dataIndex) {
                    // 將每個儲存格的文字置中
                    $(row).find('td').css({
                        'white-space': 'nowrap',  // 防止換行
                        'text-align': 'center'    // 置中
                    });
                },
                columns: [
                    { data: 'method' },
                    { data: 'stock1' },
                    { data: 'stock2' },
                    { data: 'start_date' },
                    { data: 'end_date' },
                    { data: 'window_size'},
                    { data: 'n_times' },
                    { data: 'track_date' },
                    {
                        className: 'dt-remove-tracking dt-center',  // 讓按鈕也置中
                        orderable: false,
                        data: null,
                        defaultContent: '<button type="button" class="btn btn-danger">Untrack</button>',
                    },
                    {
                        className: 'dt-run-analysis dt-center',  // 讓按鈕也置中
                        orderable: false,
                        data: null,
                        defaultContent: `<button type="button" class="btn btn-success">Results</button>`,
                    },
                ],
                order: [[1, 'asc']],  // 依 stock2 排序
            });
                    
            $('#monitor tbody').on('click', 'td.dt-remove-tracking', function () {
                var row = table.row($(this).parents('tr'));
                var data = row.data();
                remove_from_track_list(data);                        
                row.remove().draw();
            });

            $('#monitor tbody').on('click', 'td.dt-run-analysis', function () {
                var row = table.row($(this).parents('tr'));
                var track_row = row.data();
                run_monitor_analysis(track_row);
                var indexCell = $(this).parents('tr').find('td').eq(9); // 獲取該行的第 9 個單元格
                indexCell.attr('id', 'target_button'); // 設置 id
                indexCell.html(`<div class="circle" id="distance_circle" align=center style="">
                                    <span class="spinner-border">
                                    </span><span class="load"></span> 
                                </div>`
                            );
            });
        }
    });
});


// 顯示stock_price的Highcharts
function renderHighchart(stockData, signalsData) {
  var stock1 = $("#stock1").val();
  var stock2 = $("#stock2").val();

  // 顯示 stock1 和 stock2 的交易信號
  Highcharts.stockChart("container", {
      rangeSelector: { selected: 1 },
      title: { text: "Stock Prices and Trading Signals" },
      yAxis: {
          title: { text: "Price" },
          gridLineColor: '#e6e6e6',
          gridLineWidth: 1,
      },
      xAxis: {
          gridLineColor: '#e6e6e6',
          gridLineWidth: 1,
      },
      series: [
          {
              name: stock1,
              data: stockData.map(item => [new Date(item.date).getTime(), item.stock1_close]),
              color: "#00BFFF",
              lineWidth: 2,
              tooltip: { valueDecimals: 2 },
          },
          {
              name: stock2,
              data: stockData.map(item => [new Date(item.date).getTime(), item.stock2_close]),
              color: "#1E90FF",
              lineWidth: 2,
              tooltip: { valueDecimals: 2 },
          },
          // Stock 1 BUY 信號
          {
              type: "scatter",
              name: "Buy (Stock 1)",
              data: signalsData.filter(signal => signal.action_stock1 === "BUY").map(signal => ({
                  x: new Date(signal.date_unix).getTime(),
                  y: signal.price_stock1,
                  marker: {
                      symbol: "triangle",
                      fillColor: "green",
                      lineColor: "green",
                      lineWidth: 2,
                      radius: 6,
                  },
              })),
              tooltip: { pointFormat: "Buy (Stock 1) - Price: {point.y}" },
          },
          // Stock 1 SELL 信號
          {
              type: "scatter",
              name: "Sell (Stock 1)",
              data: signalsData.filter(signal => signal.action_stock1 === "SELL").map(signal => ({
                  x: new Date(signal.date_unix).getTime(),
                  y: signal.price_stock1,
                  marker: {
                      symbol: "triangle-down",
                      fillColor: "red",
                      lineColor: "red",
                      lineWidth: 2,
                      radius: 6,
                  },
              })),
              tooltip: { pointFormat: "Sell (Stock 1) - Price: {point.y}" },
          },
          // Stock 2 BUY 信號
          {
              type: "scatter",
              name: "Buy (Stock 2)",
              data: signalsData.filter(signal => signal.action_stock2 === "BUY").map(signal => ({
                  x: signal.date_unix,
                  y: signal.price_stock2,
                  marker: {
                      symbol: "triangle",
                      fillColor: "green",
                      lineColor: "green",
                      lineWidth: 2,
                      radius: 6,
                  },
              })),
              tooltip: { pointFormat: "Buy (Stock 2) - Price: {point.y}" },
          },
          // Stock 2 SELL 信號
          {
              type: "scatter",
              name: "Sell (Stock 2)",
              data: signalsData.filter(signal => signal.action_stock2 === "SELL").map(signal => ({
                  x: signal.date_unix,
                  y: signal.price_stock2,
                  marker: {
                      symbol: "triangle-down",
                      fillColor: "red",
                      lineColor: "red",
                      lineWidth: 2,
                      radius: 6,
                  },
              })),
              tooltip: { pointFormat: "Sell (Stock 2) - Price: {point.y}" },
          }
      ],
  });

}   
// 設置 Highcharts 並渲染 spread 的圖形
function renderSpreadChart(spreadData, upperLineData, lowerLineData, middleLineData, signalsData) {    
    Highcharts.stockChart("spreadContainer", {
        rangeSelector: {
            selected: 1,
        },
        title: {
            text: "Spread and Trading Signals",
        },
        yAxis: {
            title: { text: "value" },
            gridLineColor: '#e6e6e6',
            gridLineWidth: 1,
        },
        xAxis: {
            gridLineColor: '#e6e6e6',
            gridLineWidth: 1,
        },
        series: [
            // Spread 的實線
            {
                name: "Spread",
                data: spreadData.map(item => [item.date, item.spread]),
                color: "black",
                lineWidth: 1,
            },
            // 上線虛線
            {
                name: "Upper Line",
                data: upperLineData.map(item => [item.date, item.upper_line !== 0 ? item.upper_line : null]),
                dashStyle: "Dash",
                color: "red",
                lineWidth: 1,
            },
            // 中線虛線
            {
                name: "Middle Line",
                data: middleLineData.map(item => [item.date, item.middle_line !== 0 ? item.middle_line : null]),
                dashStyle: "Dash",
                color: "blue",
                lineWidth: 1,
            },
            // 下線虛線
            {
                name: "Lower Line",
                data: lowerLineData.map(item => [item.date, item.lower_line !== 0 ? item.lower_line : null]),
                dashStyle: "Dash",
                color: "green",
                lineWidth: 1,
            },
            // 交易訊號 (開倉或關倉)
            {
                type: "scatter",
                name: "Trading Signals",
                data: signalsData.map(signal => ({
                    x: signal.date_unix,
                    y: signal.spread,
                    marker: {
                        symbol: signal.action_stock1 === "BUY" ? "triangle" : "triangle-down", // 判斷是買還是賣
                        fillColor: signal.action_stock1 === "BUY" ? "green" : "red",
                        lineColor: signal.action_stock1 === "BUY" ? "green" : "red",
                        lineWidth: 2,
                        radius: 6,
                    }
                })),
                tooltip: {
                    pointFormat: 'Spread: {point.y}, Action: {point.action_stock1}, Stock1: {point.action_stock1}, Stock2: {point.action_stock2}',
                },
            },
        ],
    });
}
// 損益圖表渲染函數
function renderProfitLossChart(profitLossData, cashData, EntryPoint, ExitPoint) {
  Highcharts.stockChart('profitLossContainer', {
      chart: {
          type: 'line'
      },
      title: {
          text: 'Profits & Loss (Percentage)'
      },
      yAxis: {
          labels: {
              formatter: function () {
                  return this.value + '%';  // Y軸顯示百分比
              }
          },
          title: {
              text: 'Percentage'
          },
          gridLineColor: '#e6e6e6',
          gridLineWidth: 1,
      },
      xAxis: {
          type: 'datetime',
          gridLineColor: '#e6e6e6',
          gridLineWidth: 1,
      },
      series: [
          {
              name: 'Daily Value',
              data: Object.entries(profitLossData).map(([date, value]) => [new Date(date).getTime(), value]),
              color: "#1E90FF",
              lineWidth: 1,
              tooltip: {
                  pointFormat: 'Daily Value: {point.y}'
              }
          },
          {
              name: 'Cash',
              data: Object.entries(cashData).map(([date, value]) => [new Date(date).getTime(), value]),
              color: "#FFA500",
              lineWidth: 1,
              tooltip: {
                  pointFormat: 'Cash: {point.y}'
              }
          },
          {
              type: "scatter",
              name: "Entry Points",
              data: EntryPoint.map(point => [point[0], point[1]]),  // 使用進場點數據
              marker: {
                  symbol: "circle",
                  fillColor: "red",
                  lineWidth: 1,
                  radius: 4
              },
              tooltip: { pointFormat: "Entry Point<br>x: {point.x}<br>y: {point.y}" }
          },
          {
              type: "scatter",
              name: "Exit Points",
              data: ExitPoint.map(point => [point[0], point[1]]),  // 使用出場點數據
              marker: {
                  symbol: "circle",
                  fillColor: "green",
                  lineWidth: 1,
                  radius: 4
              },
              tooltip: { pointFormat: "Exit Point<br>x: {point.x}<br>y: {point.y}" }
          },
      ],
      rangeSelector: {
          selected: 1
      }
  });
}
  
function renderDatatable(signalsData, stock1, stock2) {
    // 首先动态设置表格标题
    $("#table-head").html(`
        <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Action of ${stock1}</th>
            <th>Price of ${stock1}</th>
            <th>Action of ${stock2}</th>
            <th>Price of ${stock2}</th>
        </tr>
    `);

    // 初始化 DataTable，确保没有多次初始化或重复数据
    $("#datatable").DataTable({
        destroy: true,  // 每次都重新加载表格
        data: signalsData.map(signal => ({
            date_original: signal.date_original,
            status: signal.status,  // Open/Close 类型
            action_stock1: signal.action_stock1,  // 正确使用 action_stock1
            price_stock1: parseFloat(signal.price_stock1).toFixed(2),  // 使用 price_stock1 数据并格式化
            action_stock2: signal.action_stock2,  // 正确使用 action_stock2
            price_stock2: parseFloat(signal.price_stock2).toFixed(2),  // 使用 price_stock2 数据并格式化
        })),
        columns: [
            { data: "date_original", title: "Date" },
            { data: "status", title: "Type" },
            { data: "action_stock1", title: `Action of ${stock1}` },
            { data: "price_stock1", title: `Price of ${stock1}` },
            { data: "action_stock2", title: `Action of ${stock2}` },
            { data: "price_stock2", title: `Price of ${stock2}` }
        ]
    });
}  

function renderDatatable2(tradeResults, stock1, stock2) {
    $("#table-head2").html(`
        <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Action of ${stock1}</th>
            <th>Price of ${stock1}</th>
            <th>Action of ${stock2}</th>
            <th>Price of ${stock2}</th>
            <th>Percentage of Profit|Loss (%)</th>
        </tr>
    `);

    $("#datatable2").DataTable({
        destroy: true,
        data: tradeResults.map(trade => ({
            date: trade.date,
            type: trade.status,  // 进场或出场
            action_stock1: trade.action_stock1,
            price_stock1: parseFloat(trade.price_stock1).toFixed(2),
            action_stock2: trade.action_stock2,
            price_stock2: parseFloat(trade.price_stock2).toFixed(2),
            percentage_profit: trade.status === 'Close' ? parseFloat(trade.percentage_profit).toFixed(2) : ''  // 仅在出场时显示利润
        })),
        columns: [
            { data: "date", title: "Date" },  // 单列日期
            { data: "type", title: "Type" },
            { data: "action_stock1", title: `Action of ${stock1}` },
            { data: "price_stock1", title: `Price of ${stock1}` },
            { data: "action_stock2", title: `Action of ${stock2}` },
            { data: "price_stock2", title: `Price of ${stock2}` },
            { data: "percentage_profit", title: "Percentage of Profit|Loss (%)" }
        ]
    });
}

// -----------技術指標----------------------------------------------

function remove_from_track_list2(track_row){

    var track_spread = new FormData;
    track_spread.append("stock1", track_row['stock1']);
    // track_spread.append("stock2", track_row['stock2']);
    track_spread.append("start_date", track_row['start_date']);
    track_spread.append("end_date", track_row['end_date']);
    track_spread.append("fastk_period", track_row['fastk_period']);
    track_spread.append("slowk_period", track_row['slowk_period']);
    track_spread.append("slowd_period", track_row['slowd_period']);
    track_spread.append("fastperiod", track_row['fastperiod']);
    track_spread.append("slowperiod", track_row['slowperiod']);
    track_spread.append("signalperiod", track_row['signalperiod']);
    track_spread.append("bb_timeperiod", track_row['bb_timeperiod']);
    track_spread.append("nbdevup", track_row['nbdevup']);
    track_spread.append("nbdevdn", track_row['nbdevdn']);
    track_spread.append("matype", track_row['matype']);
    track_spread.append("rsi_timeperiod", track_row['rsi_timeperiod']);
    track_spread.append("dmi_timeperiod", track_row['dmi_timeperiod']);
    track_spread.append("stop_loss_percentage", track_row['stop_loss_percentage']);
    track_spread.append("max_recover_days", track_row['max_recover_days']);
    track_spread.append("consider_optimization", track_row['consider_optimization']);
    track_spread.append("critical_value", track_row['critical_value']);
    track_spread.append("consider_p_value", track_row['consider_p_value']);
    track_spread.append("track_date", track_row['track_date']);

    $.ajax({
      url: "/monitor1/remove_track/",
      data:track_spread, 
      type:'POST',
      dataType: 'json',
      processData:false,
      contentType:false,
      success:function(data)
      {
        alert("Remove successfully!");
      }
    });
}

function run_monitor_analysis2(track_row){
    var track_spread = new FormData;
    track_spread.append("stock1", track_row['stock1']);
    // track_spread.append("stock2", track_row['stock2']);
    track_spread.append("start_date", track_row['start_date']);
    track_spread.append("end_date", track_row['end_date']);
    track_spread.append("fastk_period", track_row['fastk_period']);
    track_spread.append("slowk_period", track_row['slowk_period']);
    track_spread.append("slowd_period", track_row['slowd_period']);
    track_spread.append("fastperiod", track_row['fastperiod']);
    track_spread.append("slowperiod", track_row['slowperiod']);
    track_spread.append("signalperiod", track_row['signalperiod']);
    track_spread.append("bb_timeperiod", track_row['bb_timeperiod']);
    track_spread.append("nbdevup", track_row['nbdevup']);
    track_spread.append("nbdevdn", track_row['nbdevdn']);
    track_spread.append("matype", track_row['matype']);
    track_spread.append("rsi_timeperiod", track_row['rsi_timeperiod']);
    track_spread.append("dmi_timeperiod", track_row['dmi_timeperiod']);


    track_spread.append("stop_loss_percentage", track_row['stop_loss_percentage']);
    track_spread.append("max_recover_days", track_row['max_recover_days']);
    track_spread.append("consider_optimization", track_row['consider_optimization']);
    track_spread.append("critical_value", track_row['critical_value']);
    track_spread.append("consider_p_value", track_row['consider_p_value']);
    track_spread.append("track_date", track_row['track_date']);

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/monitor1/run_tracker/",
        data: track_spread,
        processData: false,
        contentType: false,
        success: function (response) {
            $('#staticBackdrop2').modal('show');
            console.log("response.data_stock_band_gc : ", response.data_stock_band_gc);
            console.log("response.data_stock_MACD_fast_gc : ", response.data_stock_MACD_fast_gc);
            console.log("response.data_stock_adx : ", response.data_stock_adx);
            var indexCell = $(`#target_button2`);
            if (indexCell.length) {
                indexCell.html(`<button type="button" class="btn btn-success">Results</button>`);
                indexCell.removeAttr('id'); // 刪除 id
            } 

            // KD
            var overboughtValue = 80;
            var oversoldValue   = 20;

            console.log("data_stock_K_gc: ", response.data_stock_K_gc);
            console.log("pattern_matches_morning: ", response.pattern_matches_morning);
            console.log("pattern_matches_evening: ", response.pattern_matches_evening);
            console.log("pattern_matches_red_3: ", response.pattern_matches_red_3);
            console.log("pattern_matches_bla_3: ", response.pattern_matches_bla_3);
            console.log("bullish_engulfing_list: ", response.bullish_engulfing_list);
            console.log("bearish_engulfing_list: ", response.bearish_engulfing_list);


            tra_figure_inductor_kd(response.data_stock_K_gc, response.data_stock_D_dc, overboughtValue, oversoldValue, response.data_stock_K, response.data_stock_D);
            // 布林帶
            tra_figure_candle_band(response.data_stock_band_gc, response.data_stock_band_dc, response.data_stock_candle, response.data_stock_Band_upper, response.data_stock_Band_mid, response.data_stock_Band_lower);
            // MACD
            tra_figure_inductor_macd(response.data_stock_MACD_fast_gc, response.data_stock_MACD_slow_dc, response.data_stock_MACD_fast, response.data_stock_MACD_slow, response.data_stock_MACD_hist)
            // RSI
            tra_figure_candle_rsi(response.data_stock_rsi, response.data_stock_ob, response.data_stock_os, response.data_stock_candle);
            // ADX
            // tra_figure_candle_adx(response.data_stock_adx, response.data_stock_candle);
            // DMI
            // tra_figure_candle_dmi(response.data_stock_dmi_gc, response.data_stock_dmi_dc, response.data_stock_dip, response.data_stock_dim, response.data_stock_candle);
            // ADX + DMI
            tra_figure_candle_adx_dmi(response.data_stock_adx, response.data_stock_dmi_gc, response.data_stock_dmi_dc, response.data_stock_dip, response.data_stock_dim, response.data_stock_candle);
            // K線型態 清晨之星 & 黃昏之星
            tra_figure_kline_star(response.data_stock_candle, response.pattern_matches_evening, response.pattern_matches_morning)
            // 紅三兵 & 黑三兵
            tra_figure_kline_three(response.data_stock_candle, response.pattern_matches_red_3, response.pattern_matches_bla_3)
            // 看漲吞噬 & 看跌吞噬
            tra_figure_kline_engulfing(response.data_stock_candle, response.bullish_engulfing_list, response.bearish_engulfing_list)
        }
      });
}

$(document).ready(function (){
    $.ajax({
        url: "/monitor1/get_track_list/",
        type: "post",
        dataType : 'json',
        processData : false,
        contentType : false,
        success: function (response) {
            console.log(response.track_data);
            var table = $("#monitor1").DataTable({
                data: response.track_data,
                "createdRow": function (row, data, dataIndex) {
                    // 將每個儲存格的文字置中
                    $(row).find('td').css({
                        'white-space': 'nowrap',  // 防止換行
                        'text-align': 'center'    // 置中
                    });
                },

                columns: [
                    { data: 'stock1' },
                    { data: 'fastk_period' },
                    { data: 'slowk_period' },
                    { data: 'slowd_period' },
                    { data: 'fastperiod' },
                    { data: 'slowperiod' },
                    { data: 'signalperiod' },
                    { data: 'bb_timeperiod' },
                    { data: 'nbdevup' },
                    { data: 'nbdevdn' },
                    { data: 'matype' },
                    { data: 'rsi_timeperiod' },
                    { data: 'dmi_timeperiod' },
                    { data: 'track_date' },
                    {
                        className: 'dt-remove-tracking dt-center',  // 讓按鈕也置中
                        orderable: false,
                        data: null,
                        defaultContent: '<button type="button" class="btn btn-danger">Untrack</button>',
                    },
                    {
                        className: 'dt-run-analysis dt-center',  // 讓按鈕也置中
                        orderable: false,
                        data: null,
                        defaultContent: `<button type="button" class="btn btn-success">Results</button>`,
                    },
                ],
                // order: [[1, 'asc']],  // 依 stock2 排序
                order: [[0, 'asc']],  // 依 stock1 排序
            });
                    
            $('#monitor1 tbody').on('click', 'td.dt-remove-tracking', function () {
                var row = table.row($(this).parents('tr'));
                var data = row.data();
                remove_from_track_list2(data);                        
                row.remove().draw();
            });

            $('#monitor1 tbody').on('click', 'td.dt-run-analysis', function () {
                var row = table.row($(this).parents('tr'));
                var track_row = row.data();
                run_monitor_analysis2(track_row);
                // console.log('track_row', track_row);
                var indexCell = $(this).parents('tr').find('td').eq(16); // 獲取該行的第 8 個單元格
                indexCell.attr('id', 'target_button2'); // 設置 id
                indexCell.html(`<div class="circle" id="distance_circle2" align=center style="">
                                    <span class="spinner-border">
                                    </span><span class="load"></span> 
                                </div>`
                            );
            });
        }
    });
});

function figure_two_monitor(data_stock, stock_name, stock_name_red, stock_name_green, sub_stock_name_red, sub_stock_name_green){
  (async () => {
      // const data = await fetch(
      //     'https://demo-live-data.highcharts.com/aapl-c.json'
      // ).then(response => response.json());

      Highcharts.stockChart('figure_two_monitor', {
          rangeSelector: {
              selected: 1
          },
  
          title: {
              text: 'Stock Price & entry point(進出場)'
          },
          
          xAxis: {
              min: Date.UTC(2021, 1, 1), // 自定义开始日期（例如：2022年1月1日）
              max: Date.UTC(2024, 1, 1) // 自定义结束日期（例如：2023年12月31日）
          },

          series: [
              {
                  name: stock_name[0],
                  data: data_stock[0],  //stock_name
                  lineWidth: 2,
                  dashStyle: 'Solid',
                  shadow: {
                      color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                      offsetX: 2, // 阴影水平偏移
                      offsetY: 2, // 阴影垂直偏移
                      opacity: 0.5 // 阴影透明度
                  },
                  marker: {
                      fillColor: 'white', // 设置标记填充颜色
                      lineColor: 'black', // 设置标记边框颜色
                      lineWidth: 1, // 设置标记边框宽度
                      states: {
                          // 鼠标悬停状态
                          hover: {
                              enabled: true, // 启用悬停效果
                          },
                      }
                  },
              },
              {
                  name: stock_name[1],
                  data: data_stock[1],  //sub_stock_name
                  lineWidth: 2,
                  dashStyle: 'Solid',
                  shadow: {
                      color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                      offsetX: 2, // 阴影水平偏移
                      offsetY: 2, // 阴影垂直偏移
                      opacity: 0.5 // 阴影透明度
                  },
                  marker: {
                      fillColor: 'white', // 设置标记填充颜色
                      lineColor: 'black', // 设置标记边框颜色
                      lineWidth: 1 ,// 设置标记边框宽度
                      states: {
                          // 鼠标悬停状态
                          hover: {
                              enabled: true, // 启用悬停效果
                          },
                      }
                  },
              },
              {
                  type: 'scatter',
                  name: 'Sell Signal',
                  data: stock_name_red, // 只为 Stock A
                  marker: {
                      symbol: 'triangle-down',
                      fillColor: 'red',
                      lineColor: 'red',
                      lineWidth: 2,
                      radius: 6,
                  },
                  visible: true,
              },
              {
                  type: 'scatter',
                  name: 'Buy Signal',
                  data: stock_name_green,
                  marker: {
                      symbol: 'triangle',
                      fillColor: 'green',
                      lineColor: 'green',
                      lineWidth: 2,
                      radius: 6,
                  },
                  visible: true,
              },
              {
                  type: 'scatter',
                  name: 'Sell Signal',
                  data: sub_stock_name_red, // 只为 Stock B
                  marker: {
                      symbol: 'triangle-down',
                      fillColor: 'red',
                      lineColor: 'red',
                      lineWidth: 2,
                      radius: 6,
                  },
                  visible: true,
              },
              {
                  type: 'scatter',
                  name: 'Sell Signal',
                  data: sub_stock_name_green, // 只为 Stock B
                  marker: {
                      symbol: 'triangle',
                      fillColor: 'green',
                      lineColor: 'green',
                      lineWidth: 2,
                      radius: 6,
                  },
                  visible: true,
              },
          ]
      });
  })();
}

function render_profit_loss_graph_monitor(
  container,
  daily_profits,
  total_values,
  entry_point,
  exit_point,
){
  // set the allowed units for data grouping
  groupingUnits = [
      [
          "week", // unit name
          [1], // allowed multiples
      ],
      ["month", [1, 2, 3, 4, 6]],
      ];
  
      var obj = {
          rangeSelector: {
              selected: 5,
          },
      
          title: {
              text: "Profits & Loss(損益圖)",
          },
      
          xAxis: {
              gridLineWidth: 1, // 設定x軸網格線的寬度
          },
      
          yAxis: [
              {
              labels: {
                  align: "right",
                  x: -6,
                  formatter: function () {
                      return (this.value).toFixed(2) + '%'; // 將數值轉換為百分比格式
                  }
              },
              title: {
                  text: "percentage",
              },
              top: "0%",
              height: "100%",
              offset: 0,
              lineWidth: 1,
              resize: {
                  enabled: true,
              },
              },
          ],
      
          tooltip: {
              split: true,
          },
      
          series: [
              {
              name: "Daily",
              data: daily_profits,
              color: "darkmagenta",
              lineWidth: 2,
              dataGrouping: {
                  units: groupingUnits,
              },
              shadow: {
                  color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                  offsetX: 2, // 阴影水平偏移
                  offsetY: 2, // 阴影垂直偏移
                  opacity: 0.5 // 阴影透明度
              },
              marker: {
                  fillColor: 'white', // 设置标记填充颜色
                  lineColor: 'black', // 设置标记边框颜色
                  lineWidth: 1 ,// 设置标记边框宽度
                  states: {
                      // 鼠标悬停状态
                      hover: {
                          enabled: true, // 启用悬停效果
                      },
                  }
              },
              },
              {
              name: "Cash",
              data: total_values,
              color: "RoyalBlue",
              lineWidth: 2,
              dataGrouping: {
                  units: groupingUnits,
              },
              shadow: {
                  color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                  offsetX: 2, // 阴影水平偏移
                  offsetY: 2, // 阴影垂直偏移
                  opacity: 0.5 // 阴影透明度
              },
              marker: {
                  fillColor: 'white', // 设置标记填充颜色
                  lineColor: 'black', // 设置标记边框颜色
                  lineWidth: 1 ,// 设置标记边框宽度
                  states: {
                      // 鼠标悬停状态
                      hover: {
                          enabled: true, // 启用悬停效果
                      },
                  }
              },
              },
              {
              type: "scatter",
              data: exit_point, // 使用傳遞的數據
              name: "Exit Point",
              marker: {
                  symbol: "circle",
                  fillColor: "green",
                  lineColor: "green",
                  name: "Exit Point",
                  enabled: true,
                  radius: 3,
              },
              visibility: true,
              },
              {
              type: "scatter",
              data: entry_point, // 使用傳遞的數據
              name: "Entry Point",
              marker: {
                  symbol: "circle",
                  fillColor: "brown",
                  lineColor: "brown",
                  name: "Entry Point",
                  enabled: true,
                  radius: 3,
              },
              visibility: true,
              },
          ],
          };
      
          Highcharts.stockChart(container, obj);
}

function render_bands_graph_monitor(
  container,
  spread,
  middle_line,
  upper_line,
  lower_line,
  bands_signals_sell,
  bands_singals_buy
){
  // set the allowed units for data grouping
  groupingUnits = [
      [
          "week", // unit name
          [1], // allowed multiples
      ],
      ["month", [1, 2, 3, 4, 6]],
      ];
  
      var obj = {
          rangeSelector: {
            selected: 5,
          },
      
          title: {
            text: "Bollinger Bands(布林通道)",
          },
      
          xAxis: {
            gridLineWidth: 1, // 設定x軸網格線的寬度
          },
      
          yAxis: [
            {
              labels: {
                align: "right",
                x: -6,
              },
              title: {
                text: "value",
              },
              top: "0%",
              height: "100%",
              offset: 0,
              lineWidth: 1,
              resize: {
                enabled: true,
              },
            },
          ],
      
          tooltip: {
            split: true,
          },
      
          series: [
            {
              name: "top",
              data: upper_line,
              color: "purple",
              lineWidth: 1,
              dashStyle: "Dash", // 線條樣式
              dataGrouping: {
                units: groupingUnits,
              },
              shadow: {
                  color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                  offsetX: 2, // 阴影水平偏移
                  offsetY: 2, // 阴影垂直偏移
                  opacity: 0.5 // 阴影透明度
              },
              marker: {
                  fillColor: 'white', // 设置标记填充颜色
                  lineColor: 'black', // 设置标记边框颜色
                  lineWidth: 1 ,// 设置标记边框宽度
                  states: {
                      // 鼠标悬停状态
                      hover: {
                          enabled: true, // 启用悬停效果
                      },
                  }
              },
            },
            {
              name: "low",
              data: lower_line,
              color: "gray",
              lineWidth: 1,
              dashStyle: "Dash", // 線條樣式
              dataGrouping: {
                units: groupingUnits,
              },
              shadow: {
                  color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                  offsetX: 2, // 阴影水平偏移
                  offsetY: 2, // 阴影垂直偏移
                  opacity: 0.5 // 阴影透明度
              },
              marker: {
                  fillColor: 'white', // 设置标记填充颜色
                  lineColor: 'black', // 设置标记边框颜色
                  lineWidth: 1 ,// 设置标记边框宽度
                  states: {
                      // 鼠标悬停状态
                      hover: {
                          enabled: true, // 启用悬停效果
                      },
                  }
              },
            },
            {
              name: "mid",
              data: middle_line,
              color: "lightblue",
              lineWidth: 1,
              dashStyle: "Dash", // 線條樣式
              dataGrouping: {
                units: groupingUnits,
              },
              shadow: {
                  color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                  offsetX: 2, // 阴影水平偏移
                  offsetY: 2, // 阴影垂直偏移
                  opacity: 0.5 // 阴影透明度
              },
              marker: {
                  fillColor: 'white', // 设置标记填充颜色
                  lineColor: 'black', // 设置标记边框颜色
                  lineWidth: 1 ,// 设置标记边框宽度
                  states: {
                      // 鼠标悬停状态
                      hover: {
                          enabled: true, // 启用悬停效果
                      },
                  }
              },
            },
            {
              name: "spread",
              data: spread,
              color: "black",
              lineWidth: 2,
              dataGrouping: {
                units: groupingUnits,
              },
              shadow: {
                  color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                  offsetX: 2, // 阴影水平偏移
                  offsetY: 2, // 阴影垂直偏移
                  opacity: 0.5 // 阴影透明度
              },
              marker: {
                  fillColor: 'white', // 设置标记填充颜色
                  lineColor: 'black', // 设置标记边框颜色
                  lineWidth: 1 ,// 设置标记边框宽度
                  states: {
                      // 鼠标悬停状态
                      hover: {
                          enabled: true, // 启用悬停效果
                      },
                  }
              },
            },

            {
              type: "scatter",
              data: bands_singals_buy, // 使用傳遞的數據
              name: "Long",
              marker: {
                symbol: "triangle",
                fillColor: "green",
                lineColor: "green",
                lineWidth: 2,
                name: "buy",
                enabled: true,
                radius: 6,
              },
              visibility: true,
            },
            {
              type: "scatter",
              data: bands_signals_sell, // 使用傳遞的數據
              name: "Short",
              marker: {
                symbol: "triangle-down",
                fillColor: "red",
                lineColor: "red",
                lineWidth: 2,
                name: "sell",
                enabled: true,
                radius: 6,
              },
              visibility: true,
            },
          ],
        };
      
        Highcharts.stockChart(container, obj);

}

// traker inductor
function tra_figure_inductor_kd(data_stock_K_gc, data_stock_D_dc, overboughtValue, oversoldValue, data_stock_D, data_stock_K){
    (async () => {        
        Highcharts.stockChart('tra_figure_inductor_kd', {
            // rangeSelector: {
            //     selected: 1
            // },
            chart: {
                alignTicks: false // 禁止轴对齐
            },

            title: {
                text: 'K & D inductor'
            },
            
            xAxis: {
                type: 'datetime', // 确保 x 轴为时间类型

            },

            yAxis: [
                {
                    // 上半部分显示 KD
                    height: '80%', // 设置占图表总高度的比例
                    // lineWidth: 2,
                    plotLines: [
                        {
                            value: overboughtValue,
                            color: 'red',
                            dashStyle: 'Dash',
                            width: 1,
                            label: {
                                text: 'Overbought',
                                align: 'right',
                                style: { color: 'red' }
                            }
                        },
                        {
                            value: oversoldValue,
                            color: 'red',
                            dashStyle: 'Dash',
                            width: 1,
                            label: {
                                text: 'Oversold',
                                align: 'right',
                                style: { color: 'red' }
                            }
                        }
                    ]
                },
            ],
            series: [
                {
                    name: 'K',
                    data: data_stock_D,  // K
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: 'D',
                    data: data_stock_K,  //sub_stock_name
                    color: 'orange',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1 ,// 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    type: "scatter",
                    data: data_stock_K_gc, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "red",
                      lineColor: "red",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: data_stock_D_dc, // 使用傳遞的數據
                    name: "DC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "green",
                      lineColor: "green",
                      lineWidth: 2,
                      name: "DC",
                      enabled: true,
                      radius: 3,
                    },
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_inductor_macd(data_stock_MACD_fast_gc, data_stock_MACD_slow_dc, data_stock_MACD_fast, data_stock_MACD_slow, data_stock_MACD_hist){
    
    (async () => {
        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-c.json'
        // ).then(response => response.json());
        console.log('in tra_figure_inductor_MACD')
        
        Highcharts.stockChart('tra_figure_inductor_MACD', {
            // rangeSelector: {
            //     selected: 1
            // },
            chart: {
                alignTicks: false // 禁止轴对齐
            },

            title: {
                text: 'MACD inductor'
            },
            
            xAxis: {
                // min: Date.UTC(2021, 1, 1), // 自定义开始日期（例如：2022年1月1日）
                // max: Date.UTC(2024, 1, 1) // 自定义结束日期（例如：2023年12月31日）
                type: 'datetime' // 确保 x 轴为时间类型
            },
            yAxis: [
                {   
                    title: {
                        text: 'MACD'
                    },
                    // 下半部分显示 MACD
                    height: '80%', // 设置占图表总高度的比例
                    lineWidth: 2,
                    // lineWidth: 2,
                }
            ],

            series: [
                // 下半部分的 MACD
                {
                    name: 'fast',
                    data: data_stock_MACD_fast,
                    // yAxis: 1, // 使用第二个 Y 轴
                    color: 'blue',
                    lineWidth: 1
                },
                {
                    name: 'slow',
                    data: data_stock_MACD_slow,
                    // yAxis: 1, // 使用第二个 Y 轴
                    color: 'orange',
                    lineWidth: 1
                },
                // {
                //     type: 'column', // 使用柱状图显示 Histogram
                //     name: 'Histogram',
                //     data: data_stock_MACD_hist,
                //     yAxis: 1, // 使用第二个 Y 轴
                //     color: 'purple'
                // }
                {
                    type: 'column', // 使用柱状图显示 Histogram
                    name: 'Histogram',
                    data: data_stock_MACD_hist, // 数据
                    // yAxis: 1, // 使用第二个 Y 轴
                    zones: [
                        {
                            value: 0, // 小于 0 的数据
                            color: 'red' // 颜色为红色
                        },
                        {
                            value: Infinity, // 大于等于 0 的数据
                            color: 'green' // 颜色为绿色
                        }
                    ],
                    color: 'green', // 默认颜色（正值）
                    negativeColor: 'red' // 负值颜色
                },
                {
                    type: "scatter",
                    data: data_stock_MACD_fast_gc, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "red",
                      lineColor: "red",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: data_stock_MACD_slow_dc, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "green",
                      lineColor: "green",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    visibility: true,
                }
            ]
        });
    })();
}

function tra_figure_candle_band(data_stock_band_gc, data_stock_band_dc, data_stock_candle, data_stock_Band_upper, data_stock_Band_mid, data_stock_Band_lower){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
    
        }
    
        // create the chart
        Highcharts.stockChart('tra_figure_inductor_band', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'AAPL Historical'
            },
    
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '100%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    name: 'up',
                    data: data_stock_Band_upper,
                    color: 'red',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: 'mid',
                    data: data_stock_Band_mid,  
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: 'low',
                    data: data_stock_Band_lower,
                    color: 'green',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    type: 'candlestick',
                    name: 'Band',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    type: "scatter",
                    data: data_stock_band_gc, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "black",
                      lineColor: "black",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: data_stock_band_dc, // 使用傳遞的數據
                    name: "DC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "DC",
                      enabled: true,
                      radius: 3,
                    },
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_candle_rsi(data_stock_rsi, data_stock_ob, data_stock_os,data_stock_candle){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
        }
    
        // create the chart
        Highcharts.stockChart('tra_figure_inductor_rsi', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'RSI'
            },
    
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '60%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
                {   
                    plotLines: [
                        {
                            value: 70,
                            color: 'red',
                            dashStyle: 'Dash',
                            width: 1,
                            label: {
                                text: 'Overbought',
                                align: 'right',
                                style: { color: 'red' }
                            }
                        },
                        {
                            value: 30,
                            color: 'red',
                            dashStyle: 'Dash',
                            width: 1,
                            label: {
                                text: 'Oversold',
                                align: 'right',
                                style: { color: 'red' }
                            }
                        }
                    ],
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'RSI'
                    },
                    top: '65%',
                    height: '35%',
                    offset: 0,
                    lineWidth: 2
                }
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'AAPL',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    yAxis: 0,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    name: 'rsi',
                    data: data_stock_rsi,  
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    type: "scatter",
                    data: data_stock_ob, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "black",
                      lineColor: "black",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    yAxis: 1,
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: data_stock_os, // 使用傳遞的數據
                    name: "DC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "DC",
                      enabled: true,
                      radius: 3,
                    },
                    yAxis: 1,
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_candle_adx(data_stock_adx, data_stock_candle){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
        }
    
        // create the chart
        Highcharts.stockChart('figure_inductor_adx', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'ADX'
            },
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '60%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
                {   
                    plotLines: [
                        {
                            value: 30,
                            color: 'red',
                            dashStyle: 'Dash',
                            width: 1,
                            label: {
                                text: 'trade',
                                align: 'right',
                                style: { color: 'red' }
                            }
                        },
                        {
                            value: 20,
                            color: 'red',
                            dashStyle: 'Dash',
                            width: 1,
                            label: {
                                text: 'no_trade',
                                align: 'right',
                                style: { color: 'red' }
                            }
                        }
                    ],
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'ADX'
                    },
                    top: '65%',
                    height: '35%',
                    offset: 0,
                    lineWidth: 2
                }
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'ADX',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    yAxis: 0,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    name: 'adx',
                    data: data_stock_adx,  
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                // {
                //     type: "scatter",
                //     data: data_stock_ob, // 使用傳遞的數據
                //     name: "GC",
                //     marker: {
                //       symbol: "triangle",
                //       fillColor: "black",
                //       lineColor: "black",
                //       lineWidth: 2,
                //       name: "GC",
                //       enabled: true,
                //       radius: 3,
                //     },
                //     yAxis: 1,
                //     visibility: true,
                // },
                // {
                //     type: "scatter",
                //     data: data_stock_os, // 使用傳遞的數據
                //     name: "DC",
                //     marker: {
                //       symbol: "triangle",
                //       fillColor: "orange",
                //       lineColor: "orange",
                //       lineWidth: 2,
                //       name: "DC",
                //       enabled: true,
                //       radius: 3,
                //     },
                //     yAxis: 1,
                //     visibility: true,
                // },
            ]
        });
    })();
}

function tra_figure_candle_dmi(data_stock_dmi_gc, data_stock_dmi_dc, data_stock_dip, data_stock_dim, data_stock_candle){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
        }
    
        // create the chart
        Highcharts.stockChart('figure_inductor_dmi', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'DMI'
            },
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '60%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
                {   
                    // plotLines: [
                    //     {
                    //         value: 30,
                    //         color: 'red',
                    //         dashStyle: 'Dash',
                    //         width: 1,
                    //         label: {
                    //             text: 'trade',
                    //             align: 'right',
                    //             style: { color: 'red' }
                    //         }
                    //     },
                    //     {
                    //         value: 20,
                    //         color: 'red',
                    //         dashStyle: 'Dash',
                    //         width: 1,
                    //         label: {
                    //             text: 'no_trade',
                    //             align: 'right',
                    //             style: { color: 'red' }
                    //         }
                    //     }
                    // ],
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'DMI'
                    },
                    top: '65%',
                    height: '35%',
                    offset: 0,
                    lineWidth: 2
                }
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'DMI',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    yAxis: 0,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    name: 'dip',
                    data: data_stock_dip,  
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: 'dim',
                    data: data_stock_dim,  
                    color: 'green',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    type: "scatter",
                    data: data_stock_dmi_dc, // 使用傳遞的數據
                    name: "DC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "DC",
                      enabled: true,
                      radius: 3,
                    },
                    yAxis: 1,
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: data_stock_dmi_gc, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "green",
                      lineColor: "green",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    yAxis: 1,
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_candle_adx_dmi(data_stock_adx, data_stock_dmi_gc, data_stock_dmi_dc, data_stock_dip, data_stock_dim, data_stock_candle){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
        }
    
        // create the chart
        Highcharts.stockChart('tra_figure_inductor_adx_dmi', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'ADX+DMI'
            },
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '60%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
                {   
                    // plotLines: [
                    //     {
                    //         value: 30,
                    //         color: 'red',
                    //         dashStyle: 'Dash',
                    //         width: 1,
                    //         label: {
                    //             text: 'trade',
                    //             align: 'right',
                    //             style: { color: 'red' }
                    //         }
                    //     },
                    //     {
                    //         value: 20,
                    //         color: 'red',
                    //         dashStyle: 'Dash',
                    //         width: 1,
                    //         label: {
                    //             text: 'no_trade',
                    //             align: 'right',
                    //             style: { color: 'red' }
                    //         }
                    //     }
                    // ],
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'DMI'
                    },
                    top: '65%',
                    height: '35%',
                    offset: 0,
                    lineWidth: 2
                }
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'DMI',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    yAxis: 0,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    name: 'adx',
                    data: data_stock_adx,  
                    color: 'black',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: 'dip',
                    data: data_stock_dip,  
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: 'dim',
                    data: data_stock_dim,  
                    color: 'green',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    type: "scatter",
                    data: data_stock_dmi_dc, // 使用傳遞的數據
                    name: "DC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "DC",
                      enabled: true,
                      radius: 3,
                    },
                    yAxis: 1,
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: data_stock_dmi_gc, // 使用傳遞的數據
                    name: "GC",
                    marker: {
                      symbol: "triangle",
                      fillColor: "green",
                      lineColor: "green",
                      lineWidth: 2,
                      name: "GC",
                      enabled: true,
                      radius: 3,
                    },
                    yAxis: 1,
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_kline_star(data_stock_candle, pattern_matches_evening, pattern_matches_morning){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
    
            // volume.push([
            //     data[i][0], // the date
            //     data[i][5] // the volume
            // ]);
        }
    
        // create the chart
        Highcharts.stockChart('tra_figure_inductor_kline_star', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'Star Historical'
            },
    
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '100%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'stock',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    type: "scatter",
                    data: pattern_matches_morning, // 使用傳遞的數據
                    name: "morning star",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "morning star",
                      enabled: true,
                      radius: 6,
                    },
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: pattern_matches_evening, // 使用傳遞的數據
                    name: "evening star",
                    marker: {
                      symbol: "triangle",
                      fillColor: "black",
                      lineColor: "black",
                      lineWidth: 2,
                      name: "evening star",
                      enabled: true,
                      radius: 6,
                    },
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_kline_three(data_stock_candle, pattern_matches_red_3, pattern_matches_bla_3){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
    
            // volume.push([
            //     data[i][0], // the date
            //     data[i][5] // the volume
            // ]);
        }
    
        // create the chart
        Highcharts.stockChart('tra_figure_inductor_kline_three', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'Three Historical'
            },
    
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '100%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'stock',
                    color: 'green',
                    upColor: 'red',
                    data: ohlc,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    type: "scatter",
                    data: pattern_matches_red_3, // 使用傳遞的數據
                    name: "morning star",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "morning star",
                      enabled: true,
                      radius: 6,
                    },
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: pattern_matches_bla_3, // 使用傳遞的數據
                    name: "evening star",
                    marker: {
                      symbol: "triangle",
                      fillColor: "black",
                      lineColor: "black",
                      lineWidth: 2,
                      name: "evening star",
                      enabled: true,
                      radius: 6,
                    },
                    visibility: true,
                },
            ]
        });
    })();
}

function tra_figure_kline_engulfing(data_stock_candle, bullish_engulfing_list, bearish_engulfing_list){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]];
    
        for (let i = 0; i < dataLength; i += 1) {
            ohlc.push([
                data_stock_candle[i][0], // the date
                data_stock_candle[i][1], // open
                data_stock_candle[i][2], // high
                data_stock_candle[i][3], // low
                data_stock_candle[i][4] // close
            ]);
    
            // volume.push([
            //     data[i][0], // the date
            //     data[i][5] // the volume
            // ]);
        }
    
        // create the chart
        Highcharts.stockChart('tra_figure_inductor_kline_engulfing', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'Engulfing Historical'
            },
    
            yAxis: [
                {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '100%',
                    lineWidth: 2,
                    resize: {
                        enabled: true
                    }
                }, 
            ],
    
            tooltip: {
                split: true
            },
    
            series: [
                {
                    type: 'candlestick',
                    name: 'stock',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    type: "scatter",
                    data: bullish_engulfing_list, // 使用傳遞的數據
                    name: "bullish_engulfing",
                    marker: {
                      symbol: "triangle",
                      fillColor: "orange",
                      lineColor: "orange",
                      lineWidth: 2,
                      name: "bullish_engulfing",
                      enabled: true,
                      radius: 6,
                    },
                    visibility: true,
                },
                {
                    type: "scatter",
                    data: bearish_engulfing_list, // 使用傳遞的數據
                    name: "bearish_engulfing",
                    marker: {
                      symbol: "triangle",
                      fillColor: "black",
                      lineColor: "black",
                      lineWidth: 2,
                      name: "bearish_engulfing",
                      enabled: true,
                      radius: 6,
                    },
                    visibility: true,
                },
            ]
        });
    })();
}