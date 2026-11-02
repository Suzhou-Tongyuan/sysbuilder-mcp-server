within SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_;
model gu_ti_fa_dong_ji_xi_tong_ "固体发动机系统"
	parameter Real zong_chang_ = 6.2;
	parameter Real zui_da_wai_jing_ = 2.4;
	parameter Real zong_zhi_liang_ = 12000;
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.ke_ti_ ke_ti_"壳体"
		annotation (Placement(transformation(origin = {110.0, 133.3},
			extent = {{-33.3, -12.0}, {33.3, 12.0}},
			rotation = 0.0)));
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.pen_guan_ pen_guan_"喷管"
		annotation (Placement(transformation(origin = {737.0, 172.3},
			extent = {{-33.3, -12.0}, {33.3, 12.0}},
			rotation = 0.0)));
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.gu_ti_ran_liao_ gu_ti_ran_liao_"固体燃料"
		annotation (Placement(transformation(origin = {94.0, 45.3},
			extent = {{-55.3, -12.0}, {55.3, 12.0}},
			rotation = 0.0)));
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.ci_fu_xi_tong_ ci_fu_xi_tong_"伺服系统"
		annotation (Placement(transformation(origin = {422.0, 177.3},
			extent = {{-55.3, -12.0}, {55.3, 12.0}},
			rotation = 0.0)));
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.yao_zhu_ yao_zhu_"药柱"
		annotation (Placement(transformation(origin = {416.0, 129.3},
			extent = {{-33.3, -12.0}, {33.3, 12.0}},
			rotation = 0.0)));
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.dian_huo_zhuang_zhi_ dian_huo_zhuang_zhi_"点火装置"
		annotation (Placement(transformation(origin = {88.0, 89.3},
			extent = {{-55.3, -12.0}, {55.3, 12.0}},
			rotation = 0.0)));
	SysbuilderRootModel.gu_ti_fa_dong_ji_xi_tong_mo_xing_._04_jie_gou_mo_xing_.L1_xi_tong_ceng_.kong_zhi_xi_tong_ kong_zhi_xi_tong_"控制系统"
		annotation (Placement(transformation(origin = {88.0, 177.3},
			extent = {{-55.3, -12.0}, {55.3, 12.0}},
			rotation = 0.0)));
	Modelica.Blocks.Interfaces.RealInput xi_tong_tui_li_shu_chu_duan_kou_"系统推力输出端口"
		annotation (Placement(transformation(origin = {0.0, 117.3},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0),
			iconTransformation(origin = {0.0, 117.3},
			extent = {{-6.0, -6.0}, {6.0, 6.0}},
			rotation = 0.0)));

	annotation (
		Diagram(coordinateSystem(extent = {{0.000000,0.000000}, {804.000000,233.333333}},
 			preserveAspectRatio = false, 
			grid = {2.0, 2.0})),
		Icon(coordinateSystem(extent = {{0.000000,0.000000}, {804.000000,233.333333}},
			 grid = {2.0, 2.0}), graphics = {
 Rectangle(
 lineColor = {255, 250, 227}, fillColor = {255, 255, 255},
 fillPattern = FillPattern.VerticalCylinder,
 extent = {{0.000000, 0.000000}, {804.000000, 233.333333}}),
  			Rectangle(
 fillColor = {255, 255, 255}, lineThickness = 1.25, 
 			 extent = {{0.000000,0.000000}, {804.000000, 233.333333}}),
			Text(
 			extent = {{0.000000,203.333333}, {804.000000, 233.333333}}, 
			textString =  "固体发动机系统", 
 			textStyle = {TextStyle.None})})); 
equation
	connect(dian_huo_zhuang_zhi_.dian_huo_shu_chu_duan_kou_,yao_zhu_.dian_huo_shu_ru_duan_kou_)
		annotation (Line(origin = {150.666667,89.333333},points = {{0.0,0.0}, {9.3,0.0}, {9.3,36.0}, {226.7,36.0}}, color = {0, 0, 255}));
	connect(yao_zhu_.ran_qi_shu_chu_duan_kou_,pen_guan_.ran_qi_shu_ru_duan_kou_)
		annotation (Line(origin = {456.000000,129.333333},points = {{0.0,0.0}, {40.0,0.0}, {40.0,42.7}, {241.3,42.7}}, color = {0, 0, 255}));
	connect(kong_zhi_xi_tong_.kong_zhi_zhi_ling_shu_chu_duan_kou_,ci_fu_xi_tong_.kong_zhi_shu_ru_duan_kou_)
		annotation (Line(origin = {150.666667,177.333333},points = {{0.0,0.0}, {212.0,0.0}}, color = {0, 0, 255}));
	connect(ci_fu_xi_tong_.zhi_xing_shu_chu_duan_kou_,pen_guan_.ci_fu_diao_jie_duan_kou_)
		annotation (Line(origin = {485.333333,177.333333},points = {{0.0,0.0}, {212.0,0.0}}, color = {0, 0, 255}));
	connect(ke_ti_.jie_gou_an_zhuang_duan_kou_,yao_zhu_.jie_gou_zhi_cheng_duan_kou_)
		annotation (Line(origin = {150.666667,133.333333},points = {{0.0,0.0}, {226.7,1.3}}, color = {0, 0, 255}));
end gu_ti_fa_dong_ji_xi_tong_;