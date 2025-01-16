$.ajaxSetup({
    headers: { "X-CSRFToken": csrf_token }, // 全局設置CSRF Token
    type: "POST", // 全局設置POST方法
});

$(document).ready(function () {
    $('#search').on('click', function (e) {
        e.preventDefault(); // 防止表單的默認提交
        var startTime = Date.now(); // 獲取提交開始的時間
        var elapsedTime = 0; // 初始化運行時間

        // 顯示加載提示框，並定時更新運行時間
        Swal.fire({
            title: 'Loading...',
            html: 'Running time: <b></b> seconds.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
                const b = Swal.getHtmlContainer().querySelector('b');
                timerInterval = setInterval(() => {
                    elapsedTime = (Date.now() - startTime) / 1000;
                    b.textContent = elapsedTime.toFixed(2);
                }, 10); // 每100ms更新一次
            }
        });

        // 獲取用戶輸入的股票代號和年份
        const ticker = $('#ticker').val();
        const year = $('#years').val();
        console.log({ ticker: ticker, year: year });

        $.ajax({
            url: '/stockpricing/', // URL對應你的views.py中的路徑
            type: 'POST',
            data: {
                ticker: ticker,
                years: year
            },
            success: function (response) {
                console.log(response); // 打印成功響應

                // 關閉加載框並顯示成功提示，包含總運行時間
                Swal.fire({
                    icon: 'success',
                    title: 'Successfully!',
                    text: 'Page load time: ' + elapsedTime.toFixed(2) + ' seconds',
                    confirmButtonText: 'Closed'
                });
                // 格式化日期
                const rawDate = response.current_price.date; // 例如 '20250113'
                const formattedDate = `${rawDate.slice(0, 4)}-${rawDate.slice(4, 6)}-${rawDate.slice(6, 8)}`;
                // 更新實時價格
                $('#current-price').text(response.current_price.price);
                $('#current-date').text(formattedDate);
                $('#current-time').text(response.current_price.time);
                
                // 渲染 Highcharts 圖表
                renderHighcharts(response);

                // 渲染表格
                renderDividendTable(response.tables.dividend_table, response.current_price.price, response.valuations, parseInt(year));
                renderHighLowTable(response.tables.high_low_table, response.current_price.price, response.valuations, parseInt(year));
                renderPbrTable(response.tables.PBR_table, response.current_price.price, response.valuations, parseInt(year));
                renderPERTable(response.tables.PER_table, response.current_price.price, response.valuations, parseInt(year));
            },
            error: function (error) {
                console.error('Error fetching strategy result:', error);
            }
        });
    });
});

function renderHighcharts(data) {
    const methods = [
        {
            method: "股利法",
            ranges: [
                { start: 0, end: data.valuations.cheap[0] || 0 },
                { start: data.valuations.cheap[0] || 0, end: data.valuations.reasonable[0] || 0 },
                { start: data.valuations.reasonable[0] || 0, end: data.valuations.expensive[0] || 0 },
                { start: data.valuations.expensive[0] || 0, end: null }
            ]
        },
        {
            method: "高低價法",
            ranges: [
                { start: 0, end: data.valuations.cheap[1] || 0 },
                { start: data.valuations.cheap[1] || 0, end: data.valuations.reasonable[1] || 0 },
                { start: data.valuations.reasonable[1] || 0, end: data.valuations.expensive[1] || 0 },
                { start: data.valuations.expensive[1] || 0, end: null }
            ]
        },
        {
            method: "本淨比法",
            ranges: [
                { start: 0, end: data.valuations.cheap[2] || 0 },
                { start: data.valuations.cheap[2] || 0, end: data.valuations.reasonable[2] || 0 },
                { start: data.valuations.reasonable[2] || 0, end: data.valuations.expensive[2] || 0 },
                { start: data.valuations.expensive[2] || 0, end: null }
            ]
        },
        {
            method: "本益比法",
            ranges: [
                { start: 0, end: data.valuations.cheap[3] || 0 },
                { start: data.valuations.cheap[3] || 0, end: data.valuations.reasonable[3] || 0 },
                { start: data.valuations.reasonable[3] || 0, end: data.valuations.expensive[3] || 0 },
                { start: data.valuations.expensive[3] || 0, end: null }
            ]
        }
    ];

    Highcharts.chart("highcharts-container", {
        chart: {
            type: "bar"
        },
        title: {
            text: "股票定價結果"
        },
        xAxis: {
            categories: ["股利法", "高低價法", "本淨比法", "本益比法"]
        },
        yAxis: {
            min: 0,
            title: {
                text: "價格區間"
            },
            plotLines: [
                {
                    color: 'black',
                    width: 4,
                    value: data.current_price.price || 0,
                    label: {
                        text: ''
                    },
                    zIndex: 5
                }
            ]
        },
        legend: {
            reversed: true
        },
        tooltip: {
            useHTML: true,
            formatter: function () {
                if (this.series.name === "最新價格") {
                    return `<b>最新價格:</b> ${data.current_price.price.toFixed(2)}`;
                }
                if (this.point) {
                    const methodIndex = this.point.index;
                    const rangeIndex = 3 - this.series.index;
                    const range = methods[methodIndex].ranges[rangeIndex];

                    if (range.end === null) {
                        return `<b>${this.series.name}</b><br>${methods[methodIndex].method}價格區間: ${range.start.toFixed(2)} 以上`;
                    } else {
                        return `<b>${this.series.name}</b><br>${methods[methodIndex].method}價格區間: ${range.start.toFixed(2)} 到 ${range.end.toFixed(2)}`;
                    }
                }
                return `<b>最新價格:</b> ${data.current_price.price.toFixed(2)}`;
            }
        },
        plotOptions: {
            series: {
                stacking: "normal"
            }
        },
        series: [
            {
                name: "昂貴價格區間",
                data: data.intervals.up_expensive || [],
                color: "pink"
            },
            {
                name: "合理到昂貴區間",
                data: data.intervals.reasonable_expensive || [],
                color: "lightgreen"
            },
            {
                name: "便宜到合理區間",
                data: data.intervals.cheap_reasonable || [],
                color: "yellow"
            },
            {
                name: "便宜價格區間",
                data: data.intervals.down_cheap || [],
                color: "lightblue"
            },
            {
                name: "最新價格",
                type: "scatter",
                data: [{ y: data.current_price }],
                color: "black",
                tooltip: {
                    pointFormatter: function () {
                        return `<b>最新價格:</b> ${data.current_price.price.toFixed(2)}`;
                    }
                }
            }
        ]
    });
}

function renderDividendTable(dividendData, current_price, valuations, years) {
    if (!dividendData || dividendData.length === 0) {
        console.error("Dividend table data is empty or undefined.");
        $('#table-container').html('<div class="alert alert-danger">No data available for the selected years.</div>');
        return;
    }

    // 限制數據範圍
    const limitedData = dividendData.slice(0, years);

    // 清空容器
    $('#table-container').empty();

    // 動態生成表格和提示
    const tableHtml = `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center" data-bs-toggle="collapse" data-bs-target="#collapse-dividend_table">
                <h5 class="mb-0">股利法 計算數據</h5>
                <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 16 16" width="1.5em" height="1.5em" style="cursor: pointer;">
                    <path fill-rule="evenodd" d="M1.5 8a.5.5 0 0 1 .5-.5h12.793l-3.647-3.646a.5.5 0 1 1 .708-.708l4.5 4.5a.5.5 0 0 1 0 .708l-4.5 4.5a.5.5 0 1 1-.708-.708L14.793 8.5H2a.5.5 0 0 1-.5-.5z"/>
                </svg>
            </div>
            <div id="collapse-dividend_table" class="collapse">
                <div class="card-body">
                    <div class="row">
                        <div class="col">
                            <h6 class="text-muted">透過當期股利或歷史平均股利乘上合理的回本時間估算股價</h6>
                            <br>
                            <h6 class="text-muted">股價 = 平均 ${years} 年股利 x 你所希望的回本期間 (以年為單位)</h6>
                            <br>
                            <div class="alert alert-warning text-center" role="alert">
                                便宜價 = 平均 ${years} 年股利 x 15年 = <b>${valuations.cheap[0].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-success text-center" role="alert">
                                合理價 = 平均 ${years} 年股利 x 20年 = <b>${valuations.reasonable[0].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-danger text-center" role="alert">
                                昂貴價 = 平均 ${years} 年股利 x 30年 = <b>${valuations.expensive[0].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-info text-center" role="alert">
                                評價: ${
                                    current_price < valuations.cheap[0].toFixed(2)
                                        ? `當前價格 (${current_price}) < 便宜價 (${valuations.cheap[0].toFixed(2)})`
                                        : current_price >= valuations.cheap[0].toFixed(2) && current_price < valuations.reasonable[0].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於便宜價 (${valuations.cheap[0].toFixed(2)}) 和 合理價 (${valuations.reasonable[0].toFixed(2)}) 之間`
                                        : current_price >= valuations.reasonable[0] && current_price < valuations.expensive[0].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於合理價 (${valuations.reasonable[0].toFixed(2)}) 和 昂貴價 (${valuations.expensive[0].toFixed(2)}) 之間`
                                        : `當前價格 (${current_price}) > 昂貴價 (${valuations.expensive[0].toFixed(2)})`
                                }
                            </div>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table id="dividend_table" class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>股利發放年度</th>
                                    <th>現金股利盈餘</th>
                                    <th>現金股利公積</th>
                                    <th>現金股利合計</th>
                                    <th>股票股利盈餘</th>
                                    <th>股票股利公積</th>
                                    <th>股票股利合計</th>
                                    <th>股利合計</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${limitedData.map(row => `
                                    <tr>
                                        <td>${row.ID}</td>
                                        <td>${row["1"]}</td>
                                        <td>${row["2"]}</td>
                                        <td>${row["3"]}</td>
                                        <td>${row["4"]}</td>
                                        <td>${row["5"]}</td>
                                        <td>${row["6"]}</td>
                                        <td>${row["7"]}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;

    $('#table_container').append(tableHtml);

    // 初始化 DataTables
    $('#dividend_table').DataTable();
}

// 渲染高低價法表格
function renderHighLowTable(highLowData, current_price, valuations, years) {
    if (!highLowData || highLowData.length === 0) {
        console.error("High-Low table data is empty or undefined.");
        $('#table-container').html('<div class="alert alert-danger">No data available for the selected years.</div>');
        return;
    }

    // 限制數據範圍
    const limitedData = highLowData.slice(0, years);

    // 清空容器
    $('#table-container').empty();

    // 動態生成表格與提示
    const tableHtml = `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center" data-bs-toggle="collapse" data-bs-target="#collapse-high_low_table">
                <h5 class="mb-0">高低價法 計算數據</h5>
                <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 16 16" width="1.5em" height="1.5em" style="cursor: pointer;">
                    <path fill-rule="evenodd" d="M1.5 8a.5.5 0 0 1 .5-.5h12.793l-3.647-3.646a.5.5 0 1 1 .708-.708l4.5 4.5a.5.5 0 0 1 0 .708l-4.5 4.5a.5.5 0 1 1-.708-.708L14.793 8.5H2a.5.5 0 0 1-.5-.5z"/>
                </svg>
            </div>
            <div id="collapse-high_low_table" class="collapse">
                <div class="card-body">
                    <div class="row">
                        <div class="col">
                            <h6 class="text-muted">透過歷史股價的平均估算股價</h6>
                            <br>
                            <h6 class="text-muted">股價 = 平均 ${years} 年股價</h6>
                            <br>
                            <div class="alert alert-warning text-center" role="alert">
                                便宜價 = 近 ${years} 年每年最低股價平均 = <b>${valuations.cheap[1].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-success text-center" role="alert">
                                合理價 = 近 ${years} 年每年平均股價平均 = <b>${valuations.reasonable[1].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-danger text-center" role="alert">
                                昂貴價 = 近 ${years} 年每年最高股價平均 = <b>${valuations.expensive[1].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-info text-center" role="alert">
                                評價: ${
                                    current_price < valuations.cheap[1].toFixed(2)
                                        ? `當前價格 (${current_price}) < 便宜價 (${valuations.cheap[1].toFixed(2)})`
                                        : current_price >= valuations.cheap[1].toFixed(2) && current_price < valuations.reasonable[1].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於便宜價 (${valuations.cheap[1].toFixed(2)}) 和 合理價 (${valuations.reasonable[1].toFixed(2)}) 之間`
                                        : current_price >= valuations.reasonable[1] && current_price < valuations.expensive[1].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於合理價 (${valuations.reasonable[1].toFixed(2)}) 和 昂貴價 (${valuations.expensive[1].toFixed(2)}) 之間`
                                        : `當前價格 (${current_price}) > 昂貴價 (${valuations.expensive[1].toFixed(2)})`
                                }
                            </div>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table id="high_low_table" class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>年度</th>
                                    <th>最高</th>
                                    <th>最低</th>
                                    <th>收盤</th>
                                    <th>平均</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${limitedData.map(row => `
                                    <tr>
                                        <td>${row.ID}</td>
                                        <td>${row["1"]}</td>
                                        <td>${row["2"]}</td>
                                        <td>${row["3"]}</td>
                                        <td>${row["4"]}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;

    $('#table_container').append(tableHtml);

    // 初始化 DataTables
    $('#high_low_table').DataTable();
}
// 渲染本淨比法表格
function renderPbrTable(pbrData, current_price, valuations, years) {
    if (!pbrData || pbrData.length === 0) {
        console.error("PBR table data is empty or undefined.");
        $('#table-container').html('<div class="alert alert-danger">No data available for the selected years.</div>');
        return;
    }

    // 限制數據範圍
    const limitedData = pbrData.slice(0, years);

    // 清空容器
    $('#table-container').empty();

    // 動態生成表格和提示
    const tableHtml = `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center" data-bs-toggle="collapse" data-bs-target="#collapse-pbr_table">
                <h5 class="mb-0">本淨比法 計算數據</h5>
                <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 16 16" width="1.5em" height="1.5em" style="cursor: pointer;">
                    <path fill-rule="evenodd" d="M1.5 8a.5.5 0 0 1 .5-.5h12.793l-3.647-3.646a.5.5 0 1 1 .708-.708l4.5 4.5a.5.5 0 0 1 0 .708l-4.5 4.5a.5.5 0 1 1-.708-.708L14.793 8.5H2a.5.5 0 0 1-.5-.5z"/>
                </svg>
            </div>
            <div id="collapse-pbr_table" class="collapse">
                <div class="card-body">
                    <div class="row">
                        <div class="col">
                            <h6 class="text-muted">透過歷史平均 PBR 乘上最新 BPS 估算股價</h6>
                            <br>
                            <h6 class="text-muted">股價 = 近 ${years} 年 PBR 平均 x 最新淨值</h6>
                            <br>
                            <div class="alert alert-warning text-center" role="alert">
                                便宜價 = 近 ${years} 年最低 PBR 平均 x 最新淨值 = <b>${valuations.cheap[3].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-success text-center" role="alert">
                                合理價 = 近 ${years} 年平均 PBR 平均 x 最新淨值 = <b>${valuations.reasonable[3].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-danger text-center" role="alert">
                                昂貴價 = 近 ${years} 年最高 PBR 平均 x 最新淨值 = <b>${valuations.expensive[3].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-info text-center" role="alert">
                                評價: ${
                                    current_price < valuations.cheap[3].toFixed(2)
                                        ? `當前價格 (${current_price}) < 便宜價 (${valuations.cheap[3].toFixed(2)})`
                                        : current_price >= valuations.cheap[3].toFixed(2) && current_price < valuations.reasonable[3].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於便宜價 (${valuations.cheap[3].toFixed(2)}) 和 合理價 (${valuations.reasonable[3].toFixed(2)}) 之間`
                                        : current_price >= valuations.reasonable[3] && current_price < valuations.expensive[3].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於合理價 (${valuations.reasonable[3].toFixed(2)}) 和 昂貴價 (${valuations.expensive[3].toFixed(2)}) 之間`
                                        : `當前價格 (${current_price}) > 昂貴價 (${valuations.expensive[3].toFixed(2)})`
                                }
                            </div>                           
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table id="pbr_table" class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>年度</th>
                                    <th>BPS(元)</th>
                                    <th>最高PBR</th>
                                    <th>最低PBR</th>
                                    <th>平均PBR</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${limitedData.map(row => `
                                    <tr>
                                        <td>${row.ID}</td>
                                        <td>${row["1"]}</td>
                                        <td>${row["2"]}</td>
                                        <td>${row["3"]}</td>
                                        <td>${row["4"]}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;

    $('#table_container').append(tableHtml);

    // 初始化 DataTables
    $('#pbr_table').DataTable();
}

// 渲染本益比法表格
function renderPERTable(PERData, current_price, valuations, years) {
    if (!PERData || PERData.length === 0) {
        console.error("PER table data is empty or undefined.");
        $('#table-container').html('<div class="alert alert-danger">No data available for the selected years.</div>');
        return;
    }

    // 限制數據範圍
    const limitedData = PERData.slice(0, years);

    // 清空容器
    $('#table-container').empty();

    // 動態生成表格與提示
    const tableHtml = `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center" data-bs-toggle="collapse" data-bs-target="#collapse-PER_table">
                <h5 class="mb-0">本益比法 計算數據</h5>
                <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 16 16" width="1.5em" height="1.5em" style="cursor: pointer;">
                    <path fill-rule="evenodd" d="M1.5 8a.5.5 0 0 1 .5-.5h12.793l-3.647-3.646a.5.5 0 1 1 .708-.708l4.5 4.5a.5.5 0 0 1 0 .708l-4.5 4.5a.5.5 0 1 1-.708-.708L14.793 8.5H2a.5.5 0 0 1-.5-.5z"/>
                </svg>
            </div>
            <div id="collapse-PER_table" class="collapse">
                <div class="card-body">
                    <div class="row">
                        <div class="col">
                            <h6 class="text-muted">透過近一年EPS和歷史平均EPS的平均乘上歷史平均PER估算股價</h6>
                            <br>
                            <h6 class="text-muted">股價 = ((近一年EPS + 近 ${years} 年平均EPS) / 2) * 近 ${years} 年PER平均</h6>
                            <br>
                            <div class="alert alert-warning text-center" role="alert">
                                便宜價 = ((近一年EPS + 近 ${years} 年平均EPS) / 2) * 近 ${years} 年最低PER平均 = <b>${valuations.cheap[2].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-success text-center" role="alert">
                                合理價 = ((近一年EPS + 近 ${years} 年平均EPS) / 2) * 近 ${years} 年平均PER平均 = <b>${valuations.reasonable[2].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-danger text-center" role="alert">
                                昂貴價 = ((近一年EPS + 近 ${years} 年平均EPS) / 2) * 近 ${years} 年最高PER平均 = <b>${valuations.expensive[2].toFixed(2)}</b>
                            </div>
                            <div class="alert alert-info text-center" role="alert">
                                評價: ${
                                    current_price < valuations.cheap[2].toFixed(2)
                                        ? `當前價格 (${current_price}) < 便宜價 (${valuations.cheap[2].toFixed(2)})`
                                        : current_price >= valuations.cheap[2].toFixed(2) && current_price < valuations.reasonable[2].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於便宜價 (${valuations.cheap[2].toFixed(2)}) 和 合理價 (${valuations.reasonable[2].toFixed(2)}) 之間`
                                        : current_price >= valuations.reasonable[2] && current_price < valuations.expensive[2].toFixed(2)
                                        ? `當前價格 (${current_price}) 位於合理價 (${valuations.reasonable[2].toFixed(2)}) 和 昂貴價 (${valuations.expensive[2].toFixed(2)}) 之間`
                                        : `當前價格 (${current_price}) > 昂貴價 (${valuations.expensive[2].toFixed(2)})`
                                }
                            </div>                            
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table id="PER_table" class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>年度</th>
                                    <th>EPS(元)</th>
                                    <th>最高PER</th>
                                    <th>最低PER</th>
                                    <th>平均PER</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${limitedData.map(row => `
                                    <tr>
                                        <td>${row.ID}</td>
                                        <td>${row["1"]}</td>
                                        <td>${row["2"]}</td>
                                        <td>${row["3"]}</td>
                                        <td>${row["4"]}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;

    $('#table_container').append(tableHtml);

    // 初始化 DataTables
    $('#PER_table').DataTable();
}
