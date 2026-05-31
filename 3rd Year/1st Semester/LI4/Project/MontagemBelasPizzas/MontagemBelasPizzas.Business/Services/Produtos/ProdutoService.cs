using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class ProdutoService
    {
        private readonly ProdutoRepository _produtoRepository;

        public ProdutoService(ProdutoRepository produtoRepository)
        {
            _produtoRepository = produtoRepository;
        }

        public async Task<Produto?> GetProdutoById(int id)
        {
            return await _produtoRepository.GetById(id);
        }

        public async Task<IEnumerable<Produto>> GetAllProdutos()
        {
            return await _produtoRepository.GetAll();
        }

        public async Task CreateProduto(Produto produto)
        {
            await _produtoRepository.Insert(produto);
        }

        public async Task UpdateProduto(Produto produto)
        {
            await _produtoRepository.Update(produto);
        }

        public async Task DeleteProduto(int id)
        {
            await _produtoRepository.Delete(id);
        }

        public async Task<IEnumerable<Produto>> GetTop3MaisVendidos()
        {
            return await _produtoRepository.GetTop3MaisVendidos();
        }
    }
}
