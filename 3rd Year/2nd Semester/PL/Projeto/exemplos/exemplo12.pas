program ListaNomes;
var
 nomes: array[1..3] of string;
 i: integer;
begin
  writeln('Introduza 3 nomes:');
  for i := 1 to 3 do
    readln(nomes[i]);

  writeln('Os nomes inseridos foram:');
  for i := 1 to 3 do
    writeln(nomes[i]);
end.
