within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model ke_ti_ "壳体"
	parameter Real chang_du_ = 5.8;
	parameter Real nei_jing_ = 2.2;
	parameter Real bi_hou_ = 0.018;
	Modelica.Blocks.Interfaces.RealInput jie_gou_an_zhuang_duan_kou_"结构安装端口"
		annotation (Placement(transformation(origin = {34.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 180.0),
			iconTransformation(origin = {34.0, 2.0},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 180.0)));

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
			textString =  "壳体", 
 			textStyle = {TextStyle.None})})); 
end ke_ti_;