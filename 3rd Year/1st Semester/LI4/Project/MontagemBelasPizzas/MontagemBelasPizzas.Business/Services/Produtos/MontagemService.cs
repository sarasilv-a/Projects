using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class MontagemService
    {
        private readonly MontagemRepository _montagemRepository;

        public MontagemService(MontagemRepository montagemRepository)
        {
            _montagemRepository = montagemRepository;
        }

        public async Task<IEnumerable<Montagem>> GetMontagensByProdutoId(int produtoId)
        {
            return await _montagemRepository.GetByProdutoId(produtoId);
        }

        public async Task CreateMontagem(Montagem montagem)
        {
            await _montagemRepository.Insert(montagem);
        }

        public async Task DeleteMontagem(int id)
        {
            await _montagemRepository.Delete(id);
        }
    }
}
