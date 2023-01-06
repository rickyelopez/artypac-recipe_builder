<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="recipe.xsl"?>
<TAGLIST>
<%
  for var in recipe.items():
    make_var(var)
%>
</TAGLIST>\
<%def name="make_var(var)">
    <TAG>
        <NAME>${var[0]}</NAME>
        <VALUE>${var[1]}</VALUE>
    </TAG>\
</%def>
