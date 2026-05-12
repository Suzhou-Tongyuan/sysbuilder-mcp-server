within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model dian_huo_zhuang_zhi_ "点火装置"
	parameter Real chang_du_ = 0.35;
	parameter Real zhi_jing_ = 0.18;
	parameter Real dian_huo_neng_liang_ = 4.5e6;
	Modelica.Blocks.Interfaces.RealInput dian_huo_shu_chu_duan_kou_"点火输出端口"
		annotation (Placement(transformation(origin = {56.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 180.0),
			iconTransformation(origin = {56.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 180.0)));

	annotation (
		Diagram(coordinateSystem(extent = {{-55.333333,-12.000000}, {55.333333,12.000000}},
 			preserveAspectRatio = false, 
			grid = {2.0, 2.0})),
		Icon(coordinateSystem(extent = {{-55.333333,-12.000000}, {55.333333,12.000000}},
			 grid = {2.0, 2.0}), graphics = {
 Rectangle(
 lineColor = {255, 250, 227}, fillColor = {255, 255, 255},
 fillPattern = FillPattern.VerticalCylinder,
 extent = {{-55.333333, -12.000000}, {55.333333, 12.000000}}),
  			Rectangle(
 fillColor = {255, 255, 255}, lineThickness = 1.25, 
 			 extent = {{-55.333333,-12.000000}, {55.333333, 12.000000}}),
			Text(
 			extent = {{-55.333333,-18.000000}, {55.333333, 12.000000}}, 
			textString =  "点火装置", 
 			textStyle = {TextStyle.None})})); 
end dian_huo_zhuang_zhi_;