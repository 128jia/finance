$.ajaxSetup({
  data: {
    csrfmiddlewaretoken: "{{ csrf_token }}",
  },
});
/////   
  function render_signals_graph(
    container,
    ticker1,
    ticker2,
    price1,
    price2,
    signals
  ) {
    // set the allowed units for data grouping
    groupingUnits = [
      [
        "week", // unit name
        [1], // allowed multiples
      ],
      ["month", [1, 2, 3, 4, 6]],
    ];
  
    let plotLinesArray = [];
    if (signals["Entry_Exit"] && signals["Entry_Exit"].length > 0) {
      for (let i = 0; i < signals["Entry_Exit"].length; i++) {
        plotLinesArray.push({
          color: signals["Entry_Exit"][i].color, // 垂直線的顏色
          width: 1, // 垂直線的寬度
          value: signals["Entry_Exit"][i].date, // 垂直線的位置（日期）
          dashStyle: "Dash", // 線條樣式
          label: {
            text: signals["Entry_Exit"][i].label, // 標籤文字
            align: "center", // 標籤對齊方式
            y: -5, // 標籤位置（向上移動）
            rotation: 0,
            style: {
              fontSize: "10px",
            },
          },
        });
      }
    }
  
    var obj = {
      rangeSelector: {
        selected: 5,
      },
  
      title: {
        text: "Price & Signals",
      },
  
      xAxis: {
        gridLineWidth: 1, // 設定x軸網格線的寬度
        plotLines: plotLinesArray,
      },
  
      yAxis: [
        {
          labels: {
            align: "right",
            x: -6,
          },
          title: {
            text: "Price",
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
          name: ticker1,
          data: price1,
          color: "black",
          lineWidth: 1,
          dataGrouping: {
            units: groupingUnits,
          },
        },
        {
          name: ticker2,
          data: price2,
          color: "black",
          lineWidth: 1,
          dataGrouping: {
            units: groupingUnits,
          },
        },
        {
          type: "scatter",
          data: signals["stock1_buy_point"], // 使用傳遞的數據
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
          data: signals["stock1_sell_point"], // 使用傳遞的數據
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
        {
          type: "scatter",
          data: signals["stock2_buy_point"], // 使用傳遞的數據
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
          data: signals["stock2_sell_point"], // 使用傳遞的數據
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
  
  function render_bands_graph(
    container,
    spread,
    middle_line,
    upper_line,
    lower_line,
    signals_sell,
    signals_buy
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
              text: "Bollinger Bands & Signals",
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
                name: "upper_line",
                data: upper_line,
                color: "red",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
              },
              {
                name: "lower_line",
                data: lower_line,
                color: "red",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
              },
              {
                name: "middle_line",
                data: middle_line,
                color: "blue",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
              },
              {
                name: "spread",
                data: spread,
                color: "black",
                lineWidth: 1,
                dataGrouping: {
                  units: groupingUnits,
                },
              },

              {
                type: "scatter",
                data: signals_buy, // 使用傳遞的數據
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
                data: signals_sell, // 使用傳遞的數據
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

  };
  
  function render_profit_loss_graph(
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
                text: "Profits & loss",
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
                name: "Daily Value",
                data: daily_profits,
                color: "blue",
                lineWidth: 1,
                dataGrouping: {
                    units: groupingUnits,
                },
                },
                {
                name: "Cash",
                data: total_values,
                color: "orange",
                lineWidth: 1,
                dataGrouping: {
                    units: groupingUnits,
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
  };
//////////////////////////////////////
  $(document).ready(function () {
      

    $("#function-tabs .nav-link").click(function () {
      // 獲取當前點擊的按鈕的 target (對應的功能區塊)
      const target = $(this).data("target");
      console.log(target);

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
      }else if(target === "#finlab"){
          loadFinlab();
      }else if(target ==="#river"){
          loadRiver();
      }
  });
        loadDistanceMethod();
  });
  //<!--Distance Method-->
  function loadDistanceMethod() {
      $('#distance_add_track').click(function(){

          // 拿取使用者選取的parames
          var stock1 = $(`#stock1-distance`).val();
          var stock2 = $("#stock2-distance").val();
          var start_date = $("#start_date-distance").val();
          var end_date = $("#end_date-distance").val();
          var window_sizes = $(`#window_size-distance`).val();
          var std = $("#std-distance").val();
      
          var track_params = new FormData();
          track_params.append("stock1", stock1);
          track_params.append("stock2", stock2);
          track_params.append("method", "distance");
          track_params.append("start_date", start_date);
          track_params.append("end_date", end_date);
          track_params.append("window_sizes", window_sizes);
          track_params.append("std", std);
      
          $.ajax({
              url: "/monitor/add_track/",
              type: "post",
              data : track_params,
              dataType : 'json',
              processData : false,
              contentType : false,
              success: function (res) {
                  alert("Add track successful!!!!!!!!!!!")
              }
          });
        });
    
        $("#distance_submit").click(function () {
          
  
      
          // $("#signals_table").DataTable({
          //     autoWidth: false,
          //     searching: false,
          //     paging: true,
          //     lengthMenu: [[5, 10, 20], [5, 10, 20]],
          //     columns: [
          //         { title: "Date" },
          //         { title: "Type" },
          //         { title: "Stock 1 Action" },
          //         { title: "Stock 1 Price" },
          //         { title: "Stock 2 Action" },
          //         { title: "Stock 2 Price" },
          //     ],
          // });
          // 拿取使用者選取的parames
          var stock1 = $(`#stock1-distance`).val();
          var stock2 = $("#stock2-distance").val();
          var start_date = $("#start_date-distance").val();
          var end_date = $("#end_date-distance").val();
          var window_sizes = $(`#window_size-distance`).val();
          var std = $("#std-distance").val();
      
          var data_config = new FormData();
          data_config.append("stock1", stock1);
          data_config.append("stock2", stock2);
          data_config.append("start_date", start_date);
          data_config.append("end_date", end_date);
          data_config.append("window_sizes", window_sizes);
          data_config.append("std", std);
      
          var date1 = new Date(start_date);
          var date2 = new Date(end_date);
          var today = new Date();
      
          var timeDifference = date2 - date1;
          var yearsDifference = timeDifference / (365 * 24 * 60 * 60 * 1000);
          if (date1 > date2) {
            alert("Error!!! Start date cannot be greater than end date");
            return;
          }
          if (yearsDifference < 1) {
            alert(
              "Error!!! The difference between start and end dates must be greater than 1 year"
            );
            return;
          }
          if (date2 > today || date1 > today) {
            alert("Error!!! The date entered cannot be greater than today");
            return;
          }
      
          $(`#distance_submit`).hide();
          $(`#distance_circle`).show();
          $(`#distance_add_track`).hide();
          $(".distance_result").css("display", "none");
      
          $.ajax({
            headers: { "X-CSRFToken": csrf_token },
            type: "POST",
            dataType: "json",
            url: "run_distance/",
            data: data_config,
            processData: false,
            contentType: false,
            success: function (response) {
              console.log(response);
      
              $(`#distance_submit`).show();
              $(`#distance_circle`).hide();
              $(`#distance_add_track`).show();
              $(".distance_result").css("display", "block");
       
              render_signals_graph(
                "signals_plot",
                response.stock1,
                response.stock2,
                response.data1_his["close"],
                response.data2_his["close"],
                response.plot_signals
              );
    
              render_bands_graph(
                "bollinger_bands_plot",
                response.spread,
                response.middle_line,
                response.upper_line,
                response.lower_line,
                response.bands_signals_sell,
                response.bands_signals_buy
              );
    
              render_profit_loss_graph(
                "profit_loss_plot",
                response.pl_daily_profits,
                response.pl_total_values,
                response.pl_entry_point,
                response.pl_exit_point,
              );
    
              $("#signals_table").DataTable({
                autoWidth: false,
                bDestroy: true,
                searching: false,
                lengthMenu: [
                  [5, 10, 20, -1],
                  [5, 10, 20, "All"],
                ],
                data: response.table_signals,
                columns: [
                  { data: "date", title: "Date" },
                  { data: "type", title: "Type" },
                  { data: "stock1_action", title: `Action of ${response.stock1}` },
                  { data: "stock1_price", title: `Price of ${response.stock1}` },
                  { data: "stock2_action", title: `Action of ${response.stock2}` },
                  { data: "stock2_price", title: `Price of ${response.stock2}` },
                ],
                columnDefs: [
                  {
                    targets: [2, 3],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "white");
                    },
                  },
                  {
                    targets: [4, 5],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "whitesmoke");
                    },
                  },
                ],
                fnRowCallback: function (nRow, aData) {
                  if (aData["type"] == "Open") {
                    $(nRow).find("td:eq(0)").css("background-color", "paleturquoise");
                    $(nRow).find("td:eq(1)").css("background-color", "paleturquoise");
                  } else {
                    $(nRow).find("td:eq(0)").css("background-color", "ime");
                    $(nRow).find("td:eq(1)").css("background-color", "ime");
                  }
                },
              });
    
              $("#exe_signals_table").DataTable({
                autoWidth: false,
                bDestroy: true,
                searching: false,
                lengthMenu: [
                  [5, 10, 20, -1],
                  [5, 10, 20, "All"],
                ],
                data: response.exe_table_signals,
                columns: [
                  { data: "date", title: "Date" },
                  { data: "type", title: "Type" },
                  { data: "stock1_action", title: `Action of ${response.stock1}` },
                  { data: "stock1_price", title: `Price of ${response.stock1}` },
                  { data: "stock2_action", title: `Action of ${response.stock2}` },
                  { data: "stock2_price", title: `Price of ${response.stock2}` },
                  { data: "percentage", title: `Percentage of Profit|Loss (%)` },
                ],
                columnDefs: [
                  {
                    targets: [2, 3],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "white");
                    },
                  },
                  {
                    targets: [4, 5],
                    createdCell: function (td, cellData, rowData, row, col) {
                      $(td).css("background-color", "whitesmoke");
                    },
                  },
                ],
                fnRowCallback: function (nRow, aData) {
                  if (aData["type"] == "Open") {
                    $(nRow).find("td:eq(0)").css("background-color", "paleturquoise");
                    $(nRow).find("td:eq(1)").css("background-color", "paleturquoise");
                  } else {
                    $(nRow).find("td:eq(0)").css("background-color", "ime");
                    $(nRow).find("td:eq(1)").css("background-color", "ime");
                  }
                },
              });
    
            
            },
          });
        });

  }


// <!-- other function  -->
function loadOtherMethod() {
  console.log("submit2 action");
  
  $(document).off("click", "#submit2").on("click", "#submit2", function (e) {
      //e.preventDefault(); // 防止表單提交的默認行為
      console.log("submit data!");
      
      // 在需要時設置 CSRF token
      const csrftoken = getCookie('csrftoken');
      console.log("CSRF Token:", csrftoken);

      $.ajax({
          url: 'rsi_cross_ajax/', // API 的 URL
          data: {
              'stock': document.getElementById('stock1').value,
              'short_rsi': document.getElementById('short_rsi').value,
              'long_rsi': document.getElementById('long_rsi').value,
              'start_date': document.getElementById('start_date').value,
              'end_date': document.getElementById('end_date').value
          },
          type: 'POST',
          headers: {
            'X-CSRFToken': csrftoken // 將 CSRF Token 添加到標頭
        },
  
          success: function (response) {
              // 渲染 Datatable
              console.log("rsi ajaxx success",response)
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

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // 如果這個 cookie 以 "name=" 開頭
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


//<!--Backtrader-->
function loadBacktrader(){
    //$(document).off("click", "#submit2").on("click", "#submit2", function (e) {
    $('#submit3').on('click', function (e) {
        e.preventDefault();  // 防止表單的默認提交
        const csrftoken = getCookie('csrftoken');
        
        $.ajax({
            url: 'run_strategy/',  // URL對應你的views.py中的路徑
            type: 'POST',
            headers: {
              'X-CSRFToken': csrftoken // 使用從 Cookie 中獲取的 CSRF Token
            },
            data: {
                stock: $('#Backtrader_stock').val(),  // 股票代號
                order_units: $('#order_units').val(),  // 單筆下單股數
                exit_strategy: $('#exit_strategy').val(),  // 出場策略
                strategy: $('#strategy').val(),  // 進場策略
                short_rsi: $('#Backtrader_short_rsi').val(),  // 短期RSI週期
                long_rsi: $('#Backtrader_long_rsi').val(),  // 長期RSI週期
                capital: $('#capital').val(),  // 初始資金
                fee: $('#fee').val(),  // 手續費
                start_date: $('#Backtrader_start_date').val(),  // 開始日期
                end_date: $('#Backtrader_end_date').val()  // 結束日期
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
// <!--finlab-->
function loadFinlab(){

}
// <!--River-->
function loadRiver(){
  $("#river_submit").on("click", function (e) {
    // 收集表單數據
    e.preventDefault();
    const stockCode = $("#stock_code").val();
    const timeUnit = $("#time_unit").val().toUpperCase(); // 轉為大寫

    // 驗證表單數據
    // if (!stockCode || !timeUnit) {
    //     alert("Stock Code 和 Time Unit 均為必填！");
    //     return;
    // }

    // 準備提交數據的結構
    const requestData = {
        stockCode: stockCode,
        timeUnit: timeUnit,
    };

    console.log("提交數據：", requestData);

    // 發送數據到伺服器
    $.ajax({
        url: "river/",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(requestData),
        success: function (response) {
            // 處理成功回應
            console.log("伺服器回應：", response);
            alert("提交成功！");
        },
        error: function (xhr, status, error) {
            // 處理錯誤回應
            console.error("提交失敗：", error);
            alert("提交失敗，請檢查網路或伺服器狀態！");
        },
    });
});
}
function renderDatatable(tradeResults) {
  $('#rsitable').DataTable({
      destroy: true,
      data: tradeResults,
      columns: [
          { title: "買賣別", data: "buy_sell" },
          { title: "買進日", data: "buy_date" },
          { title: "買進價格", data: "buy_price" },
          { title: "賣出日", data: "sell_date" },
          { title: "賣出價格", data: "sell_price" },
          { title: "買賣股數", data: "trade_units" },
          { title: "獲利", data: "profit" },
          { title: "累計獲利", data: "cumulative_profit" }
      ],
      paging: true,
      searching: true,
      ordering: true,
      lengthMenu: [10, 25, 50],
  });
}

// 渲染報酬率和最大回撤圖表
function renderProfitDrawdownChart(data) {
  Highcharts.stockChart('container', {
      title: {
          text: 'backtest'
      },

      xAxis: {
          type: 'datetime',
      },
      yAxis: {
          title: {
              text: '報酬率/最大回撤'
          },
          opposite: true // 将Y轴移到右侧
      }, 
      series: [{
          name: '報酬率',
          data: data.map(item => {
              const date = new Date(item.date); // 檢查這裡是否返回正確的日期
              return [date.getTime(), item.profit]; // 使用 getTime() 確保返回的是毫秒格式
          }),
          tooltip: {
              valueDecimals: 2
          }
      }, {
          name: '最大回撤',
          data: data.map(item => [new Date(item.date).getTime(), item.dd]),
          tooltip: {
              valueDecimals: 2
          }
      }]
  });
}

function renderNewChart(buyDates, sellDates, ohlc, volume) {

  Highcharts.stockChart('container2', {
      rangeSelector: {
          selected: 15
      },
      chart: {
          type: 'candlestick'
      },
      title: {
          text: 'Stock Chart'
      },
      xAxis: {
          type: 'datetime'
      },
      yAxis: [{
          title: {
              text: 'OHLC'
          },
      }, {
          title: {
              text: 'Volume'
          },
          top: '70%',
          height: '30%',
      }],
      series: [{
          type: 'candlestick',
          name: 'Price Data',
          data: ohlc, // 資料應包含 [time, open, high, low, close]
          tooltip: {
              valueDecimals: 2
          }
      }, {
          type: 'column',
          name: 'Volume',
          data: volume, // 資料應包含 [time, volume]
          yAxis: 1,
          tooltip: {
              valueDecimals: 0
          }
      }, {
          type: 'flags',
          name: 'Buy Signals',
          data: buyDates.map(date => ({
              x: new Date(date).getTime(),  // 将日期转换为时间戳
              title: 'B'  // 标记为 "B" 表示买入信号
          })),
          shape: 'circlepin',
          width: 16,
          tooltip: {
              pointFormat: 'Buy Signal'
          },
          stackDistance: 10, // 控制每个标记之间的距离，减少拥挤
          allowOverlapX: false, // 禁止信号点横向重叠
      }, {
          type: 'flags',
          name: 'Sell Signals',
          data: sellDates.map(date => ({
              x: new Date(date).getTime(),  // 将日期转换为时间戳
              title: 'S'  // 标记为 "S" 表示卖出信号
          })),
          shape: 'circlepin',
          width: 16,
          tooltip: {
              pointFormat: 'Sell Signal'
          },
          stackDistance: 10,
          allowOverlapX: false, 
      }]
  });
}

// 渲染績效數據
function renderPerformanceMetrics(metrics) {
  const metricsHtml = `
      <table style="width: 100%; border-collapse: collapse;">
          <tr style = "text-align: center;">
              <th>總績效</th>
              <th>交易次數</th>
              <th>平均績效</th>
              <th>平均持有天數</th>
              <th>勝率</th>
              <th>平均獲利</th>
              <th>平均虧損</th>
              <th>賺賠比</th>
              <th>期望值</th>
              <th>獲利平均持有天數</th>
              <th>虧損平均持有天數</th>
              <th>最大連續虧損</th>
              <th>最大資金回落</th>
          </tr>
          <tr style = "text-align: center;">
              <td>${metrics.total_return}</td>
              <td>${metrics.trade_count}</td>
              <td>${metrics.average_return}</td>
              <td>${metrics.average_hold_days}</td>
              <td>${metrics.win_rate}</td>
              <td>${metrics.average_profit}</td>
              <td>${metrics.average_loss}</td>
              <td>${metrics.risk_reward_ratio}</td>
              <td>${metrics.expectancy}</td>
              <td>${metrics.profit_avg_hold_days}</td>
              <td>${metrics.loss_avg_hold_days}</td>
              <td>${metrics.max_consecutive_loss}</td>
              <td>${metrics.max_drawdown}</td>
          </tr>
      </table>

  `;
  $('#performance-table').html(metricsHtml);  // 更新績效表格內容
}