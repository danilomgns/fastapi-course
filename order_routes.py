from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItemPedido
from typing import List

order_router = APIRouter(prefix="/order", tags=["orders"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def orders():
  """
  Essa é a rota padrão de autenticação de pedidos. Todas as rotas de pedidos precisam de autenticação
  """
  return {
    "mensagem": "Você acessou a minha API, na rota de pedidos"
  }

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
  novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
  session.add(novo_pedido)
  session.commit()
  return {"mensagem": f"Pedido criado com sucesso. Id do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  
  if (not usuario.admin) and (usuario.id != pedido.usuario):
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa modificação. Usuario: {usuario.id}, Admin: {usuario.admin}")

  pedido.status = "CANCELADO"
  session.commit()
  return {
    "mensagem": f"Pedido n° {pedido.id} cancelado com sucesso",
    "pedido": pedido
  }

@order_router.get("/listar")
async def listar_pedidos(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
  if not usuario.admin:
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa operação. Usuario: {usuario.id}, Admin: {usuario.admin}")
  else:
    pedidos = session.query(Pedido).all()
  
  return {
    "pedidos": pedidos
  }

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
  
  pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  elif (not usuario.admin) and (usuario.id != pedido.usuario):
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa modificação. Usuario: {usuario.id}, Admin: {usuario.admin}")
  
  item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)

  session.add(item_pedido)
  pedido.calcular_preco()
  session.commit()

  return {
    "mensagem": "Item criado com sucesso",
    "item_id": item_pedido.id,
    "preco_pedido": pedido.preco
  }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
  
  item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
  pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()

  if not item_pedido:
    raise HTTPException(status_code=400, detail="Item no pedido não existente")
  elif (not usuario.admin) and (usuario.id != pedido.usuario):
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa modificação. Usuario: {usuario.id}, Admin: {usuario.admin}")

  session.delete(item_pedido)
  pedido.calcular_preco()
  session.commit()

  return {
    "mensagem": "Item removido com sucesso",
    "item_id": item_pedido.id,
    "quantidade_skus": len(pedido.itens),
    "pedido": pedido
  }

@order_router.post("/pedido/finalizar/{id_pedido}")
def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  
  if (not usuario.admin) and (usuario.id != pedido.usuario):
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa modificação. Usuario: {usuario.id}, Admin: {usuario.admin}")

  pedido.status = "FINALIZADO"
  session.commit()
  return {
    "mensagem": f"Pedido n° {pedido.id} finalizado com sucesso",
    "pedido": pedido
  }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  
  if (not usuario.admin) and (usuario.id != pedido.usuario):
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa modificação. Usuario: {usuario.id}, Admin: {usuario.admin}")
  
  return {
    "quantidade_skus": len(pedido.itens),
    "pedido": pedido
  }

@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
  if not usuario.admin:
    raise HTTPException(status_code=400, detail=f"Você não tem autorização para fazer essa operação. Usuario: {usuario.id}, Admin: {usuario.admin}")
  else:
    pedidos_usuario = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
  
  return pedidos_usuario