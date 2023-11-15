    def learn(self, batch, batch_size=None, repeat=1, **kwargs):
        self._batch = batch_size
        r = batch.returns
        if self._rew_norm and r.std() > self.__eps:
            batch.returns = (r - r.mean()) / r.std()
        losses, actor_losses, vf_losses, ent_losses = [], [], [], []
        for _ in range(repeat):
            for b in batch.split(batch_size):
                self.optim.zero_grad()
                dist = self(b).dist
                v = self.critic(b.obs)
                a = torch.tensor(b.act, device=v.device)
                r = torch.tensor(b.returns, device=v.device)
                a_loss = -(dist.log_prob(a) * (r - v).detach()).mean()
                vf_loss = F.mse_loss(r[:, None], v)
                ent_loss = dist.entropy().mean()
                loss = a_loss + self._w_vf * vf_loss - self._w_ent * ent_loss
                loss.backward()
                if self._grad_norm:
                    nn.utils.clip_grad_norm_(
                        self.model.parameters(), max_norm=self._grad_norm)
                self.optim.step()
                actor_losses.append(a_loss.item())
                vf_losses.append(vf_loss.item())
                ent_losses.append(ent_loss.item())
                losses.append(loss.item())
        return {
            'loss': losses,
            'loss/actor': actor_losses,
            'loss/vf': vf_losses,
            'loss/ent': ent_losses,
        }