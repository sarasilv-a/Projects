program LeArray;
var
  valores: array[1..3] of integer;
  i, total: integer;
begin
  total := 0;
  for i := 1 to 3 do
    readln(valores[i]);

  for i := 1 to 3 do
    total := total + valores[i];

  writeln('Total: ', total)
end.
