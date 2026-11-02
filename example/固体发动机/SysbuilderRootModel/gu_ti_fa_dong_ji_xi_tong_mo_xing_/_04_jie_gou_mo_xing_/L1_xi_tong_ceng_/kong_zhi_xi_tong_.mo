within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model kong_zhi_xi_tong_ "控制系统"
	parameter Real ji_xiang_chang_du_ = 0.48;
	parameter Real ji_xiang_kuan_du_ = 0.32;
	parameter Real ji_suan_pin_shuai_ = 200;
	Modelica.Blocks.Interfaces.RealInput kong_zhi_zhi_ling_shu_chu_duan_kou_"控制指令输出端口"
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
			textString =  "控制系统", 
 			textStyle = {TextStyle.None})})); 
end kong_zhi_xi_tong_;