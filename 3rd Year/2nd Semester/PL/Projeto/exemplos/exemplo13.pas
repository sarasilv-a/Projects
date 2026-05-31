program ParOuImpar;
var
  num: integer;
  par: boolean;
begin
  num := 4;
  par := (num mod 2) = 0;
  if par then
    writeln(num, ' é par')
  else
    writeln(num, ' é ímpar')
end.
