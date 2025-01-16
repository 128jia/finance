

$(document).ready(function () {

    $('#distance_add_track1').click(function(){
    
        console.log("Loading add tracker ...");
        // 拿取使用者選取的parames
        var stock1         = $(`#stock_id`).val();
        // var stock2  = $("#sub_stock_id").val();
        var start_date     = $("#start-date").val();
        var end_date       = $("#end-date").val();

        // KD 3個參數
        var fastk_period   = $("#fastk_period").val();
        var slowk_period   = $("#slowk_period").val();
        var slowd_period   = $("#slowd_period").val();
        
        // MACD 3個參數
        var fastperiod     = $("#fastperiod").val();
        var slowperiod     = $("#slowperiod").val();
        var signalperiod   = $("#signalperiod").val();
        
        // 布林通道 4個參數
        var bb_timeperiod  = $("#bb_timeperiod").val();
        var nbdevup        = $("#nbdevup").val();
        var nbdevdn        = $("#nbdevdn").val();
        var matype         = $("#matype").val();
        
        // RSI 1個參數
        var rsi_timeperiod = $("#rsi_timeperiod").val();

        // DMI 1個參數
        var dmi_timeperiod = $("#dmi_timeperiod").val();
        // var window_sizes = 200;
        //var std = 2;
        // var method = 'tracker';

        var track_params = new FormData();
        track_params.append("stock1", stock1);
        // track_params.append("stock2", stock2);
        // track_params.append("method", method);
        track_params.append("start_date", start_date);
        track_params.append("end_date", end_date);
        // KD
        track_params.append("fastk_period", fastk_period);
        track_params.append("slowk_period", slowk_period);
        track_params.append("slowd_period", slowd_period);
        // MACD
        track_params.append("fastperiod", fastperiod);
        track_params.append("slowperiod", slowperiod);
        track_params.append("signalperiod", signalperiod);
        // Band
        track_params.append("bb_timeperiod", bb_timeperiod);
        track_params.append("nbdevup", nbdevup);
        track_params.append("nbdevdn", nbdevdn);
        track_params.append("matype", matype);
        // RSI
        track_params.append("rsi_timeperiod", rsi_timeperiod);
        // DMI
        track_params.append("dmi_timeperiod", dmi_timeperiod);

        // track_params.append("window_sizes", window_sizes);
        // track_params.append("std", std);

        // console.log(stock1);
        // console.log(method);
        // console.log(start_date);
        // console.log(end_date);

        console.log(fastk_period);
        console.log(slowk_period);
        console.log(slowd_period);
        console.log(fastperiod);
        console.log(slowperiod);
        console.log(signalperiod);
        console.log(bb_timeperiod);
        console.log(nbdevup);
        console.log(nbdevdn);
        console.log(matype);
        console.log(rsi_timeperiod);
        console.log(dmi_timeperiod);
        // console.log(window_sizes);
        // console.log(std);

        $.ajax({
            url: "/monitor1/add_track/",
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

        
    });

    // 預設載入 Distance Method
    loadInductorMethod()
});




function loadInductorMethod() {
    console.log("Loading Inductor Method...");
    $("#submit_inductor").on("click", function (e) {
        e.preventDefault(); // 防止表單提交的默認行為
        var overboughtValue = 80
        var oversoldValue = 20
        $.ajax({
            url: '/web_tool/inductor/', // API 的 URL
            type: 'POST',
            data: {
                'stock_inductor': document.getElementById('stock_inductor').value,
                'start_date_inductor': document.getElementById('start_date_inductor').value,
                'end_date_inductor': document.getElementById('end_date_inductor').value,
                'day': document.getElementById('day').value,
                'overbought': overboughtValue,
                'oversold': oversoldValue
            },
            success: function (response) {
                console.log("success!");

                const smallerTimestamps = new Set(response.data_stock_HighVolume.map(item => item[0]));
                const filteredLargerList = response.data_stock_df_vol.filter(item => !smallerTimestamps.has(item[0]));

                console.log(response.data_stock_HighVolume);
                console.log(response.data_stock_vol_df_5dayvol);
                console.log(response.filteredLargerList);
                console.log(response.data_stock_candle_d_day);   

                const data_table_all_value = response.data_stock_HighVolume;

                // 轉換成dict，時間戳為key，值為value
                const volDict = Object.fromEntries(
                    response.data_stock_vol_df_5dayvol.map(([timestamp, value]) => [Math.floor(timestamp), value])
                );
        
                // 將同日期的值添加進入
                data_table_all_value.forEach(item => {
                    const timestamp = item[0]; // 讀時間戳
                    if (volDict[timestamp]) {
                        item.push(volDict[timestamp]); // 添加value
                    }
                });

                // datatable
                const tableContainer = document.getElementById('highVolumeTableContainer');
                const button = this;
                const formattedData = data_table_all_value.map(item => {
                    const date = new Date(item[0]).toISOString().slice(0, 10); // 轉日期
                    return [date, item[1], item[2]];
                });

                // 一開始先隱藏表格
                if (tableContainer.style.display === 'none') {
                    tableContainer.style.display = 'block'; 

                    // 初始化 DataTable
                    $('#highVolumeTable').DataTable({
                        data: formattedData,
                        columns: [
                            { title: "Date" },
                            { title: "High Volume" },
                            { title: "Five Day MA" }
                        ]
                    });

                    button.textContent = 'Hide Table'; 
                } else {
                    tableContainer.style.display = 'none';
                    button.textContent = 'Show Table'; 
                }
                // d_day成交量
                figure_candle_d_day_sma(response.data_stock_HighVolume, response.data_stock_vol_df_5dayvol, filteredLargerList, response.data_stock_candle_d_day)
                
            },
            error: function (error) {
                console.error('Error fetching RSI cross trade data:', error);
            }
        });
    });
}

function figure_inductor_kd(data_stock_K_gc, data_stock_D_dc, overboughtValue, oversoldValue, data_stock_D, data_stock_K){
    
    (async () => {        
        Highcharts.stockChart('figure_inductor_kd', {
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
                // {
                //     name: "rsv",
                //     data: data_stock_RSV,
                //     color: "lightblue",
                //     lineWidth: 0.5,
                //     dashStyle: "Dash", // 線條樣式
                //     shadow: {
                //         color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                //         offsetX: 2, // 阴影水平偏移
                //         offsetY: 2, // 阴影垂直偏移
                //         opacity: 0.5 // 阴影透明度
                //     },
                //     marker: {
                //         fillColor: 'white', // 设置标记填充颜色
                //         lineColor: 'black', // 设置标记边框颜色
                //         lineWidth: 1 ,// 设置标记边框宽度
                //         states: {
                //             // 鼠标悬停状态
                //             hover: {
                //                 enabled: true, // 启用悬停效果
                //             },
                //         }
                //     },
                // },
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

function figure_inductor_macd(data_stock_MACD_fast_gc, data_stock_MACD_slow_dc, data_stock_MACD_fast, data_stock_MACD_slow, data_stock_MACD_hist){
    
    (async () => {
        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-c.json'
        // ).then(response => response.json());
        console.log('in figure_inductor_MACD')
        
        Highcharts.stockChart('figure_inductor_macd', {
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
            // yAxis: {
            //     title: {
            //         text: 'Values'
            //     },
            //     plotLines: [ // 添加虚线
            //         {
            //             value: 80, // Y轴上的位置
            //             color: 'red', // 虚线颜色
            //             dashStyle: 'Dash', // 虚线样式
            //             width: 1, // 虚线宽度
            //             label: {
            //                 text: 'Overbought (80)', // 标签内容
            //                 align: 'right', // 标签位置
            //                 style: {
            //                     color: 'red'
            //                 }
            //             }
            //         },
            //         {
            //             value: 20, // Y轴上的位置
            //             color: 'red', // 虚线颜色
            //             dashStyle: 'Dash', // 虚线样式
            //             width: 1, // 虚线宽度
            //             label: {
            //                 text: 'Oversold (20)', // 标签内容
            //                 align: 'right', // 标签位置
            //                 style: {
            //                     color: 'red'
            //                 }
            //             }
            //         }
            //     ]
            // },

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

function figure_candle_band(data_stock_band_gc, data_stock_band_dc, data_stock_candle, data_stock_Band_upper, data_stock_Band_mid, data_stock_Band_lower){
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
        Highcharts.stockChart('figure_inductor_band', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'Historical'
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
                // {
                //     labels: {
                //         align: 'right',
                //         x: -3
                //     },
                //     title: {
                //         text: 'Volume'
                //     },
                //     top: '65%',
                //     height: '35%',
                //     offset: 0,
                //     lineWidth: 2
                // }
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
                    name: 'AAPL',
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
                // {
                //     type: 'column',
                //     name: 'Volume',
                //     data: volume,
                //     yAxis: 1,
                //     dataGrouping: {
                //         units: groupingUnits
                //     }
                // }
            ]
        });
    })();
}

function figure_candle_rsi(data_stock_rsi, data_stock_ob, data_stock_os,data_stock_candle){
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
        Highcharts.stockChart('figure_inductor_rsi', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'RSI'
            },
    
            // yAxis: [
            //     {
            //         labels: {
            //             align: 'right',
            //             x: -3
            //         },
            //         title: {
            //             text: 'OHLC'
            //         },
            //         height: '100%',
            //         lineWidth: 2,
            //         resize: {
            //             enabled: true
            //         }
            //     }, 
            // ],
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

function figure_candle_adx(data_stock_adx, data_stock_candle){
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

function figure_candle_dmi(data_stock_dmi_gc, data_stock_dmi_dc, data_stock_dip, data_stock_dim, data_stock_candle){
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

function figure_candle_adx_dmi(data_stock_adx, data_stock_dmi_gc, data_stock_dmi_dc, data_stock_dip, data_stock_dim, data_stock_candle){
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
        Highcharts.stockChart('figure_inductor_adx_dmi', {
            
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

function figure_kline_star(data_stock_candle, pattern_matches_evening, pattern_matches_morning){
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
        Highcharts.stockChart('figure_inductor_kline_star', {
            
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

function figure_kline_three(data_stock_candle, pattern_matches_red_3, pattern_matches_bla_3){
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
        Highcharts.stockChart('figure_inductor_kline_three', {
            
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

function figure_kline_engulfing(data_stock_candle, bullish_engulfing_list, bearish_engulfing_list){
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
        Highcharts.stockChart('figure_inductor_kline_engulfing', {
            
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

// 爆大量d日量能均線 
function figure_candle_d_day_sma(data_stock_HighVolume, data_stock_vol_df_5dayvol, data_stock_df_vol, data_stock_candle_d_day){
    (async () => {

        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-ohlcv.json'
        // ).then(response => response.json());
    
        // split the data set into ohlc and volume
        const ohlc = [],
            // volume = [],
            dataLength = data_stock_candle_d_day.length,
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
                data_stock_candle_d_day[i][0], // the date
                data_stock_candle_d_day[i][1], // open
                data_stock_candle_d_day[i][2], // high
                data_stock_candle_d_day[i][3], // low
                data_stock_candle_d_day[i][4] // close
            ]);
        }
        
        // create the chart
        Highcharts.stockChart('figure_inductor_d_day_sma', {
            
            rangeSelector: {
                selected: 4
            },
    
            title: {
                text: 'D_day_sma'
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
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'energy'
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
                    name: 'stock',
                    color: 'red',
                    upColor: 'green',
                    data: ohlc,
                    yAxis: 0,
                    dataGrouping: {
                        units: groupingUnits
                    }
                },
                {
                    name: 'ma',
                    data: data_stock_vol_df_5dayvol,  
                    color: 'blue',
                    lineWidth: 1,
                    dashStyle: 'Solid',
                    yAxis: 1,
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)',
                        offsetX: 2, 
                        offsetY: 2, 
                        opacity: 0.5 
                    },
                    marker: {
                        fillColor: 'white',
                        lineColor: 'black', 
                        lineWidth: 1, 
                        states: {
                            hover: {
                                enabled: true,
                            },
                        }
                    },
                },
                {
                    type: 'column', // 柱狀圖 Histogram
                    name: 'Volume',
                    data: data_stock_df_vol,
                    yAxis: 1, 
                    zones: [
                        {
                            value: Infinity, 
                            color: 'lightgray' 
                        }
                    ],

                },
                {
                    type: 'column', // 使用柱状图显示 Histogram
                    name: 'Volume',
                    data: data_stock_HighVolume,
                    yAxis: 1,
                    zones: [
                        {
                            value: Infinity,
                            color: 'red' 
                        }
                    ],
                },
            ]
        });
    })();
}

