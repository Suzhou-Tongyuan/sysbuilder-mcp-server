within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model gu_ti_ran_liao_ "固体燃料"
	parameter Real zhuang_yao_zhi_liang_ = 8600;
	parameter Real ping_jun_mi_du_ = 1780;
	parameter Real ran_su_xi_shu_ = 0.005;
	Modelica.Blocks.Interfaces.RealInput ran_shao_gong_gei_duan_kou_"燃烧供给端口"
		annotation (Placement(transformation(origin = {-56.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {-56.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

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
			textString =  "固体燃料", 
 			textStyle = {TextStyle.None})})); 
end gu_ti_ran_liao_;