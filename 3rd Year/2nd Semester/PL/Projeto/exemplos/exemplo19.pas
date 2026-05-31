program ContemLetraA;
var
    texto: string;
    i: integer;
    encontrou: boolean;
begin
    writeln('Introduza uma string:');
    readln(texto);

    encontrou := false;
    i := 1;
    while (i <= length(texto)) and (not encontrou) do
    begin
        if texto[i] = 'a' then
            encontrou := true;
        i := i + 1;
    end;

    if encontrou then
        writeln('Contém a letra a.')
    else
        writeln('Não contém a letra a.');
end.
