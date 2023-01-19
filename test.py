from app.storage.fake_storage import FakeBranchStorage, FakeCommitStorage
from app.models import Branch, Commit

import puan
import puan.logic.plog as pg
# model0 = pg.All(
#     pg.Xor(*"xyz"),
#     pg.XNor(
#         puan.variable('A'),
#         pg.All(*"abc"),
#     )
# )

model1 = pg.All(
    pg.Xor(*"xy"),
    pg.XNor(
        puan.variable('A'),
        pg.All(*"bcd"),
    )
)
print(model1.to_b64())

# commits = [
#     Commit(
#         parent=None,
#         author="Rikard",
#         data=model0.to_b64(),
#     ),
# ]

# branches = [
#     Branch(
#         name="main",
#         commit_id=commits[0].hash(),
#         model_id="volvo"
#     )
# ]

# models = [
#     Model(
#         id="volvo",
#         name="Volvo Cars",
#         branches=[
#             "main"
#         ]
#     )
# ]

# branch_storage = FakeBranchStorage()
# commit_storage = FakeCommitStorage()

# for m in models:
#     model_storage.update(m)

# for b in branches:
#     branch_storage.update(b)

# for c in commits:
#     commit_storage.update(c)