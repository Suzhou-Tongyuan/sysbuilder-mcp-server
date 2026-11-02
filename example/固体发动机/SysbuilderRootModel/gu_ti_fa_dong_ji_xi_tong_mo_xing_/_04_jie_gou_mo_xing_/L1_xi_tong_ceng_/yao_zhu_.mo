within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model yao_zhu_ "药柱"
	parameter Real chang_du_ = 5.0;
	parameter Real nei_kong_zhi_jing_ = 0.56;
	parameter Real wai_jing_ = 2.1;
	Modelica.Blocks.Interfaces.RealInput dian_huo_shu_ru_duan_kou_"点火输入端口"
		annotation (Placement(transformation(origin = {-34.0, -4.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-34.0, -4.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

	Modelica.Blocks.Interfaces.RealInput ran_qi_shu_chu_duan_kou_"燃气输出端口"
		annotation (Placement(transformation(origin = {33.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 180.0),
			iconTransformation(origin = {33.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 180.0)));

	Modelica.Blocks.Interfaces.RealInput jie_gou_zhi_cheng_duan_kou_"结构支撑端口"
		annotation (Placement(transformation(origin = {-34.0, 6.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-34.0, 6.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

	annotation (
		Diagram(coordinateSystem(extent = {{-33.333333,-12.000000}, {33.333333,12.000000}},
 			preserveAspectRatio = false, 
			grid = {2.0, 2.0})),
		Icon(coordinateSystem(extent = {{-33.333333,-12.000000}, {33.333333,12.000000}},
			 grid = {2.0, 2.0}), graphics = {
 Rectangle(
 lineColor = {255, 250, 227}, fillColor = {255, 255, 255},
 fillPattern = FillPattern.VerticalCylinder,
 extent = {{-33.333333, -12.000000}, {33.333333, 12.000000}}),
  			Rectangle(
 fillColor = {255, 255, 255}, lineThickness = 1.25, 
 			 extent = {{-33.333333,-12.000000}, {33.333333, 12.000000}}),
			Text(
 			extent = {{-33.333333,-18.000000}, {33.333333, 12.000000}}, 
			textString =  "药柱", 
 			textStyle = {TextStyle.None})})); 
end yao_zhu_;