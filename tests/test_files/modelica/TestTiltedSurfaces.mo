within ;
model TestTiltedSurfaces
  "Test model to check impact on different tilted surfaces"
  AixLib.BoundaryConditions.SolarIrradiation.DirectTiltedSurface verWalDir[4](til={
        1.5707963267949,1.5707963267949,1.5707963267949,1.5707963267949}, azi={0,
        1.5707963267949,3.1415926535898,4.7123889803847})
    "Vertical wall all directions"
    annotation (Placement(transformation(extent={{-20,40},{0,60}})));
  AixLib.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(filNam=filNam)
    annotation (Placement(transformation(extent={{-60,0},{-40,20}})));
  AixLib.BoundaryConditions.SolarIrradiation.DirectTiltedSurface flaRooDir[4](til={0,
        0,0,0}, azi={0,1.5707963267949,3.1415926535898,4.7123889803847})
    "flat roof all directions"
    annotation (Placement(transformation(extent={{-20,0},{0,20}})));
  AixLib.BoundaryConditions.SolarIrradiation.DirectTiltedSurface tilRooDir[4](til={
        0.78539816339745,0.78539816339745,0.78539816339745,0.78539816339745},
      azi={0,1.5707963267949,3.1415926535898,4.7123889803847})
    "tilted roof all directions"
    annotation (Placement(transformation(extent={{-20,80},{0,100}})));
  parameter String filNam="D:/UnknownStationID_20150101_20151231_Aachen.mos"
    "Name of weather data file";
  Modelica.Blocks.Interfaces.RealOutput HDirTilRoo[4] "Radiation per unit area"
    annotation (Placement(transformation(extent={{100,80},{120,100}})));
  Modelica.Blocks.Interfaces.RealOutput HDirVerWal[4] "Radiation per unit area"
    annotation (Placement(transformation(extent={{100,38},{120,58}})));
  Modelica.Blocks.Interfaces.RealOutput HDirFlaRoo[4] "Radiation per unit area"
    annotation (Placement(transformation(extent={{100,0},{120,20}})));
  AixLib.BoundaryConditions.SolarIrradiation.DiffusePerez        verWalDif[4](til={
        1.5707963267949,1.5707963267949,1.5707963267949,1.5707963267949}, azi={0,
        1.5707963267949,3.1415926535898,4.7123889803847})
    "Vertical wall all directions"
    annotation (Placement(transformation(extent={{-20,-62},{0,-42}})));
  AixLib.BoundaryConditions.SolarIrradiation.DiffusePerez        flaRooDif[4](til={0,
        0,0,0}, azi={0,1.5707963267949,3.1415926535898,4.7123889803847})
    "flat roof all directions"
    annotation (Placement(transformation(extent={{-20,-100},{0,-80}})));
  AixLib.BoundaryConditions.SolarIrradiation.DiffusePerez        tilRooDif[4](til={
        0.78539816339745,0.78539816339745,0.78539816339745,0.78539816339745},
      azi={0,1.5707963267949,3.1415926535898,4.7123889803847})
    "tilted roof all directions"
    annotation (Placement(transformation(extent={{-20,-30},{0,-10}})));
  Modelica.Blocks.Interfaces.RealOutput HDifTilRoo[4]
    "Radiation per unit area"
    annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput HDifVerWal[4]
    "Radiation per unit area"
    annotation (Placement(transformation(extent={{100,-64},{120,-44}})));
  Modelica.Blocks.Interfaces.RealOutput HDifFlaRoo[4]
    "Radiation per unit area"
    annotation (Placement(transformation(extent={{100,-100},{120,-80}})));
equation
  for i in 1:4 loop
  connect(tilRooDif[i].weaBus, weaDat.weaBus) annotation (Line(
      points={{-20,-20},{-30,-20},{-30,10},{-40,10}},
      color={255,204,51},
      thickness=0.5));
  connect(verWalDif[i].weaBus, weaDat.weaBus) annotation (Line(
      points={{-20,-52},{-30,-52},{-30,10},{-40,10}},
      color={255,204,51},
      thickness=0.5));
  connect(flaRooDif[i].weaBus, weaDat.weaBus) annotation (Line(
      points={{-20,-90},{-30,-90},{-30,10},{-40,10}},
      color={255,204,51},
      thickness=0.5));
    connect(weaDat.weaBus, verWalDir[i].weaBus) annotation (Line(
        points={{-40,10},{-24,10},{-24,50},{-20,50}},
        color={255,204,51},
        thickness=0.5));
    connect(weaDat.weaBus, flaRooDir[i].weaBus) annotation (Line(
        points={{-40,10},{-20,10}},
        color={255,204,51},
        thickness=0.5));
    connect(weaDat.weaBus, tilRooDir[i].weaBus) annotation (Line(
        points={{-40,10},{-24,10},{-24,90},{-20,90}},
        color={255,204,51},
        thickness=0.5));
  end for;
  connect(tilRooDir.H, HDirTilRoo)
    annotation (Line(points={{1,90},{110,90}}, color={0,0,127}));
  connect(flaRooDir.H, HDirFlaRoo)
    annotation (Line(points={{1,10},{110,10}}, color={0,0,127}));
  connect(verWalDir.H, HDirVerWal) annotation (Line(points={{1,50},{102,50},{102,
          46},{106,46},{106,48},{110,48}}, color={0,0,127}));
  connect(tilRooDif.H, HDifTilRoo)
    annotation (Line(points={{1,-20},{110,-20}},  color={0,0,127}));
  connect(flaRooDif.H, HDifFlaRoo)
    annotation (Line(points={{1,-90},{110,-90}},  color={0,0,127}));
  connect(verWalDif.H, HDifVerWal) annotation (Line(points={{1,-52},{102,-52},{102,
          -56},{106,-56},{106,-54},{110,-54}}, color={0,0,127}));

  annotation (
    uses(                         Modelica(version="4.0.0"), AixLib(version=
            "3.0.0")),
    experiment(
      StopTime=86400,
      Interval=60.0001,
      __Dymola_Algorithm="Dassl"));
end TestTiltedSurfaces;
