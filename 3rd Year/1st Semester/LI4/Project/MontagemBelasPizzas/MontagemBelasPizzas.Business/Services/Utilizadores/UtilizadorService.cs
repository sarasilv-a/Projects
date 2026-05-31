using MontagemBelasPizzas.Data.Entities.Utilizadores;
using MontagemBelasPizzas.Data.Repositories.Utilizadores;
using BCrypt.Net;

namespace MontagemBelasPizzas.Business.Services.Utilizadores;

public class UtilizadorService
{
    private readonly UtilizadorRepository _utilizadorRepository;

    public UtilizadorService(UtilizadorRepository utilizadorRepository)
    {
        _utilizadorRepository = utilizadorRepository;
    }

    public async Task<Utilizador?> GetUtilizadorById(int id)
    {
        return await _utilizadorRepository.GetById(id);
    }

    public async Task<IEnumerable<Utilizador>> GetAllUtilizadores()
    {
        return await _utilizadorRepository.GetAll();
    }

    public async Task UpdateUtilizador(Utilizador utilizador)
    {
        await _utilizadorRepository.Update(utilizador);
    }

    public async Task DeleteUtilizador(int id)
    {
        await _utilizadorRepository.Delete(id);
    }

    public async Task<Utilizador?> ValidateCredentials(int id, string senha)
    {
        Console.WriteLine(id);
        var utilizador = await _utilizadorRepository.GetById(id);

        if (utilizador == null) return null;

        if (id == 1 && utilizador.Senha ==  senha)
        {
            return utilizador;
        }

        if (BCrypt.Net.BCrypt.Verify(senha, utilizador.Senha))
        {
            return utilizador;
        }

        return null;
    }
    
    public async Task AddUtilizador(Utilizador utilizador)
    {
        await _utilizadorRepository.Insert(utilizador);
    }

    public async Task IncrementarPizzasRejeitadas(int id)
    {
        await _utilizadorRepository.IncrementarPizzasRejeitadas(id);
    }

}

