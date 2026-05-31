program NumeroNoIntervalo;
var
    num: integer;
begin
    writeln('Introduza um número:');
    readln(num);

    if (num >= 10) and (num <= 100) then
        writeln('Está no intervalo [10, 100].')
    else
        writeln('Fora do intervalo.');
end.
