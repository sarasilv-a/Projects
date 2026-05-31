using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class IngredienteService
    {
        private readonly IngredienteRepository _ingredienteRepository;

        public IngredienteService(IngredienteRepository ingredienteRepository)
        {
            _ingredienteRepository = ingredienteRepository;
        }

        public async Task<Ingrediente?> GetIngredienteById(int id)
        {
            return await _ingredienteRepository.GetById(id);
        }

        public async Task<IEnumerable<Ingrediente>> GetAllIngredientes()
        {
            return await _ingredienteRepository.GetAll();
        }

        public async Task CreateIngrediente(Ingrediente ingrediente)
        {
            await _ingredienteRepository.Insert(ingrediente);
        }

        public async Task UpdateIngrediente(Ingrediente ingrediente)
        {
            await _ingredienteRepository.Update(ingrediente);
        }

        public async Task DeleteIngrediente(int id)
        {
            await _ingredienteRepository.Delete(id);
        }
    }
}
