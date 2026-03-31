/**
 * @name Sentinel-1 Lake Baikal Ice Validation (Spring Balanced Edition)
 * @description 交互式 Sentinel-1 SAR 影像目视解译 UI。
 * 自动在融冰期 (4月-6月) 均衡撒点，并支持一键导出验证结果。
 */

// ================= 1. 核心参数设置 =================

// 【重要】替换为你的 Asset 路径
var baikalAssetPath = "projects/baikal-466906/assets/Baikal"; 

// 设置验证年份 (例如 2015将覆盖 2015.04, 2015.05, 2015.06)
var startYear = 2015; 

// 每个月你想验证的采样点数量 (4月, 5月, 6月各取这么多)
var pointsPerMonth = 60; 

// 每张有效 SAR 影像上撒几个点
var pointsPerImage = 3; 

// ================= 2. 数据准备与通用函数 =================

var lakeROI = ee.FeatureCollection(baikalAssetPath);
var lakeGeometry = lakeROI.geometry();

// 通用影像预处理：中值滤波去噪并计算 VV-VH 比值
var processImage = function(img) {
  var smooth = img.focal_median(50, 'circle', 'meters');
  var ratio = smooth.select('VV').subtract(smooth.select('VH')).rename('Ratio');
  return smooth.addBands(ratio)
    .set('date_string', img.date().format('YYYY-MM-dd'))
    .set('img_id_clean', img.id());
};

// 通用撒点函数 (带强力湖区几何交集约束)
var sampleByDateRange = function(startDate, endDate, limitCount) {
  var s1 = ee.ImageCollection("COPERNICUS/S1_GRD")
    .filterBounds(lakeGeometry)
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filterDate(startDate, endDate)
    .sort('system:time_start'); 

  var col = s1.map(processImage);
  var imagesList = col.toList(40); // 选取该月前40张影像撒点
  
  var pointsList = imagesList.map(function(img) {
    img = ee.Image(img);
    // 强制几何求交，确保点在湖内
    var intersectionGeo = img.geometry().intersection(lakeGeometry, 100); 
    
    var pts = ee.FeatureCollection.randomPoints({
      region: intersectionGeo, 
      points: pointsPerImage, 
      seed: 123
    });
    
    return pts.map(function(pt) {
      return pt.set({
        'imgID': img.get('img_id_clean'),
        'date': img.get('date_string'),
        'timestamp': img.get('system:time_start')
      });
    });
  });
  
  return ee.FeatureCollection(pointsList).flatten().limit(limitCount);
};

// ================= 3. 分月均衡采样逻辑 (Spring Edition) =================

var generateBalancedPoints = function() {
  var ptsApr = sampleByDateRange(ee.Date.fromYMD(startYear, 4, 1), ee.Date.fromYMD(startYear, 5, 1), pointsPerMonth);
  var ptsMay = sampleByDateRange(ee.Date.fromYMD(startYear, 5, 1), ee.Date.fromYMD(startYear, 6, 1), pointsPerMonth);
  var ptsJun = sampleByDateRange(ee.Date.fromYMD(startYear, 6, 1), ee.Date.fromYMD(startYear, 7, 1), pointsPerMonth);
  
  // 合并并按时间戳排序
  return ptsApr.merge(ptsMay).merge(ptsJun).sort('timestamp');
};

// ================= 4. UI 界面 (瓦片极速渲染版) =================

Map.setOptions('SATELLITE');
Map.centerObject(lakeGeometry, 7);

var mainPanel = ui.Panel({
  style: {width: '320px', padding: '8px', backgroundColor: 'rgba(255, 255, 255, 0.95)'}
});
ui.root.insert(0, mainPanel);

mainPanel.add(ui.Label('🌱 春季均衡验证 (4/5/6月)', {fontWeight: 'bold', fontSize: '18px', color: '#2e7d32'}));
mainPanel.add(ui.Label('目标: ' + startYear + '年 4-6月 (每月' + pointsPerMonth + '点)', {fontSize: '11px', color: 'gray'}));

var startButton = ui.Button('▶️ 生成春季样本', function() {
  mainPanel.add(ui.Label('正在分月采样 (Apr, May, Jun)...', {color: 'gray'}));
  try {
    var points = generateBalancedPoints();
    points.evaluate(function(fc) {
      if (!fc || fc.features.length === 0) {
        mainPanel.add(ui.Label('⚠️ 生成失败，请检查该年份是否有可用数据。', {color: 'red'}));
        return;
      }
      startValidation(fc.features);
    });
  } catch (e) {
    mainPanel.add(ui.Label('错误: ' + e, {color: 'red'}));
  }
});
mainPanel.add(startButton);

// 验证录入逻辑
var savedResults = [];
var currentIndex = 0;

function startValidation(features) {
  mainPanel.clear();
  var progressLabel = ui.Label('进度: 1 / ' + features.length, {fontWeight: 'bold'});
  mainPanel.add(progressLabel);
  var infoLabel = ui.Label('', {fontSize: '13px', margin: '5px 0'}); 
  mainPanel.add(infoLabel);

  var showNext = function() {
    if (currentIndex >= features.length) { finishTask(); return; }
    var feat = features[currentIndex];
    var pointGeom = ee.Geometry.Point(feat.geometry.coordinates);
    
    progressLabel.setValue('进度: ' + (currentIndex + 1) + ' / ' + features.length);
    infoLabel.setValue('📅 ' + feat.properties.date);
    
    var localRegion = pointGeom.buffer(3000); 
    var img = ee.Image("COPERNICUS/S1_GRD/" + feat.properties.imgID);
    img = processImage(img).clip(localRegion);
    
    Map.layers().reset();
    // 春天使用略微明亮的显示参数以突显碎冰
    var visParams = {bands: ['VV', 'VH', 'Ratio'], min: [-25, -30, 0], max: [-5, -10, 15]};
    
    Map.addLayer(img, visParams, 'Spring Ice RGB');
    Map.addLayer(pointGeom, {color: 'red'}, '验证点');
    Map.centerObject(pointGeom, 13);
  };

  var record = function(val) {
    var feat = features[currentIndex];
    savedResults.push({
      'date': feat.properties.date,
      'lat': feat.geometry.coordinates[1],
      'lon': feat.geometry.coordinates[0],
      'manual_label': val,
      'img_id': feat.properties.imgID
    });
    currentIndex++;
    showNext();
  };

  var btnGrid = ui.Panel({layout: ui.Panel.Layout.flow('horizontal')});
  
  // 按钮配色微调
  var btnIce = ui.Button('🧊 冰', function() { record(1); });
  btnIce.style().set({backgroundColor: '#b3e5fc'});
  
  var btnWater = ui.Button('💧 水', function() { record(0); });
  btnWater.style().set({backgroundColor: '#006064', color: 'white'});
  
  var btnSkip = ui.Button('❓ 跳过/未知', function() { record(-1); });
  
  btnGrid.add(btnIce);
  btnGrid.add(btnWater);
  btnGrid.add(btnSkip);
  mainPanel.add(btnGrid);
  
  showNext();
}

function finishTask() {
  mainPanel.clear();
  mainPanel.add(ui.Label('✅ 春季验证完成!', {fontWeight: 'bold', color: 'green'}));
  var resultFC = ee.FeatureCollection(savedResults.map(function(d) { return ee.Feature(null, d); }));
  mainPanel.add(ui.Button('📥 导出CSV (Spring)', function() {
    Export.table.toDrive({
      collection: resultFC, description: 'Baikal_Spring_Balanced_' + startYear, fileFormat: 'CSV',
      selectors: ['date', 'manual_label', 'lat', 'lon', 'img_id']
    });
  }));
}
