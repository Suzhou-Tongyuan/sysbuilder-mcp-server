within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model ci_fu_xi_tong_ "伺服系统"
	parameter Real xing_cheng_ = 0.12;
	parameter Real xiang_ying_shi_jian_ = 0.08;
	parameter Real e_ding_niu_ju_ = 350;
	Modelica.Blocks.Interfaces.RealInput kong_zhi_shu_ru_duan_kou_"控制输入端口"
		annotation (Placement(transformation(origin = {-54.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-54.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

	Modelica.Blocks.Interfaces.RealInput zhi_xing_shu_chu_duan_kou_"执行输出端口"
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
			textString =  "伺服系统", 
 			textStyle = {TextStyle.None})})); 
end ci_fu_xi_tong_;