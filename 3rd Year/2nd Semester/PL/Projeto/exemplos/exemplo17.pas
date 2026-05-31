program InfoString;
var
  palavra: string;
  len: integer;
begin
  palavra := 'ola';
  len := length(palavra);
  writeln('Tamanho: ', len);
  writeln('Primeira letra: ', palavra[1])
end.
