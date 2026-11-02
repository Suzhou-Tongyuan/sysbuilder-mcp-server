within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model pen_guan_ "喷管"
	parameter Real hou_jing_ = 0.42;
	parameter Real chu_kou_zhi_jing_ = 1.15;
	parameter Real kuo_zhang_bi_ = 7.5;
	Modelica.Blocks.Interfaces.RealInput ran_qi_shu_ru_duan_kou_"燃气输入端口"
		annotation (Placement(transformation(origin = {-35.0, 0.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-35.0, 0.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

	Modelica.Blocks.Interfaces.RealInput ci_fu_diao_jie_duan_kou_"伺服调节端口"
		annotation (Placement(transformation(origin = {-35.0, 7.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-35.0, 7.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

	Modelica.Blocks.Interfaces.RealInput tui_li_shu_chu_duan_kou_"推力输出端口"
		annotation (Placement(transformation(origin = {-35.0, -7.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-35.0, -7.0},
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
			textString =  "喷管", 
 			textStyle = {TextStyle.None})})); 
end pen_guan_;