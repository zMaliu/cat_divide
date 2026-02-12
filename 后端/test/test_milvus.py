import os
import sys
import time
import unittest
from typing import Any, Dict, List, Optional


def _make_vector(dim: int, seed: int) -> List[float]:
    x = seed % 2147483647
    out: List[float] = []
    for _ in range(dim):
        x = (1103515245 * x + 12345) % 2147483647
        out.append(float(x) / 2147483647.0)
    return out


def _print_step(title: str, lines: List[str]) -> None:
    print("\n" + "=" * 72, flush=True)
    print(f"[STEP] {title}", flush=True)
    for line in lines:
        print(f"- {line}", flush=True)


def _vector_preview(v: Any, max_items: int = 5) -> Any:
    if isinstance(v, list):
        if len(v) <= max_items:
            return v
        return {"len": len(v), "head": v[:max_items]}
    return v

def _brief_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row.get("id"),
        "cat_id": row.get("cat_id"),
        "user_id": row.get("user_id"),
        "image_path": row.get("image_path"),
        "created_at": row.get("created_at"),
    }



class TestMilvusCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        os.environ.setdefault("MILVUS_HOST", "localhost")
        os.environ.setdefault("MILVUS_PORT", "19530")
        os.environ.setdefault("VECTOR_COLLECTION_NAME", "cat_vectors_test")
        os.environ.setdefault("VECTOR_DIMENSION", "8")

        from app.vector_infra.milvus.vector_respository import MilvusVectorRepository

        cls.repo = MilvusVectorRepository()
        if not cls.repo.is_available():
            raise unittest.SkipTest("Milvus 不可用或未启动")

        cls.dim = int(os.environ["VECTOR_DIMENSION"])

        cls.repo.collection.load()
        cls._ensure_initial_data()

    @classmethod
    def _query_all(cls, limit: int = 50) -> List[Dict[str, Any]]:
        output_fields = ["id", "cat_id", "user_id", "image_path", "created_at", "vector"]
        expr = "cat_id >= 0"
        try:
            rows = cls.repo.collection.query(expr, output_fields=output_fields, limit=limit)
        except TypeError:
            rows = cls.repo.collection.query(expr, output_fields=output_fields)
            rows = rows[:limit]
        normalized: List[Dict[str, Any]] = []
        for r in rows:
            item = dict(r)
            item["vector"] = _vector_preview(item.get("vector"))
            normalized.append(item)
        normalized.sort(key=lambda x: (x.get("created_at", 0), str(x.get("id", ""))))
        return normalized

    @classmethod
    def _snapshot(cls, label: str, preview_limit: int = 5) -> Dict[str, Any]:
        cls.repo.collection.load()
        rows_all = cls._query_all(limit=2000)
        return {
            "label": label,
            "collection": os.environ.get("VECTOR_COLLECTION_NAME"),
            "stats_num_entities": int(getattr(cls.repo.collection, "num_entities", 0)),
            "queried_count": len(rows_all),
            "rows_preview": [_brief_row(r) for r in rows_all[:preview_limit]],
        }

    @classmethod
    def _ensure_initial_data(cls) -> None:
        snap_before = cls._snapshot("Milvus 初始快照（插入前）")
        _print_step(
            "Milvus 初始数据（插入前）",
            [
                f"collection={snap_before['collection']}",
                f"stats_num_entities={snap_before['stats_num_entities']} (仅供参考)",
                f"queried_count={snap_before['queried_count']}",
                f"rows_preview={snap_before['rows_preview']}",
            ],
        )

        if snap_before["queried_count"] > 0:
            _print_step("初始数据检查", ["集合已有数据，跳过插入初始数据"])
            return

        now = int(time.time())
        ids = [f"init_vec_{now}_{i}" for i in range(2)]
        vectors = [_make_vector(cls.dim, 100 + i) for i in range(2)]
        metadatas = [
            {
                "id": ids[i],
                "cat_id": 9000 + i,
                "user_id": 8000 + i,
                "image_path": f"/tmp/init_{ids[i]}.jpg",
                "created_at": now + i,
            }
            for i in range(2)
        ]
        ok = cls.repo.insert(vectors, metadatas)
        exists = [cls.repo.get_by_id(vid) is not None for vid in ids]
        snap_after = cls._snapshot("Milvus 初始快照（插入后）")
        _print_step(
            "插入初始数据",
            [
                f"ok={ok}",
                f"insert_count={len(ids)}",
                f"insert_ids={ids}",
                f"inserted_rows_readback={exists}",
                f"after.queried_count={snap_after['queried_count']}",
                f"after.rows_preview={snap_after['rows_preview']}",
            ],
        )
        if not ok:
            raise AssertionError("初始数据插入失败")
        if not all(exists):
            raise AssertionError("初始数据插入后回读失败")

    def _analyze_counts(self, before: Dict[str, Any], after: Dict[str, Any], expected_delta: int) -> List[str]:
        delta = after["queried_count"] - before["queried_count"]
        lines = [
            f"before.queried_count={before['queried_count']}",
            f"after.queried_count={after['queried_count']}",
            f"delta={delta}, expected_delta={expected_delta}",
        ]
        if delta == expected_delta:
            lines.append("count_check=PASS")
        else:
            lines.append("count_check=FAIL (可能是查询limit/flush时序/并发写入导致)")
        return lines

    def test_crud(self):
        now = int(time.time())

        ids = [f"test_vec_{now}_{i}" for i in range(3)]
        vectors = [_make_vector(self.dim, i + 1) for i in range(3)]
        metadatas = [
            {
                "id": ids[i],
                "cat_id": 1000 + i,
                "user_id": 2000 + i,
                "image_path": f"/tmp/test_{ids[i]}.jpg",
                "created_at": now + i,
            }
            for i in range(3)
        ]

        snap_start = self._snapshot("CRUD 开始快照")
        _print_step(
            "CRUD 开始：Milvus 当前数据",
            [
                f"collection={snap_start['collection']}",
                f"queried_count={snap_start['queried_count']}",
                f"rows_preview={snap_start['rows_preview']}",
            ],
        )

        before_insert = self._snapshot("Insert 前")
        _print_step(
            "增（Insert）",
            [
                f"will_insert_count={len(metadatas)}",
                f"ids={ids}",
                f"vector_dim={self.dim}",
                f"before.rows_preview={before_insert['rows_preview']}",
            ],
        )
        ok = self.repo.insert(vectors, metadatas)
        after_insert = self._snapshot("Insert 后")
        inserted_exists = [self.repo.get_by_id(vid) is not None for vid in ids]
        _print_step(
            "增（Insert）结果 + 正确性分析",
            [
                f"ok={ok}",
                f"inserted_rows_readback={inserted_exists}",
                *self._analyze_counts(before_insert, after_insert, expected_delta=3),
                f"after.rows_preview={after_insert['rows_preview']}",
            ],
        )
        self.assertTrue(ok)
        self.assertTrue(all(inserted_exists))

        _print_step("查（Get by id）", [f"id={ids[0]}"])
        got = self.repo.get_by_id(ids[0])
        got_for_print: Optional[Dict[str, Any]] = _brief_row(got) if got else None
        _print_step(
            "查（Get by id）结果 + 正确性分析",
            [
                f"found={got is not None}",
                f"row={got_for_print}",
                "check=PASS (found=True 且字段匹配断言通过)" if got is not None else "check=FAIL (未查到记录)",
            ],
        )
        self.assertIsNotNone(got)
        self.assertEqual(got["id"], ids[0])
        self.assertEqual(got["cat_id"], 1000)
        self.assertEqual(got["user_id"], 2000)
        self.assertEqual(got["image_path"], f"/tmp/test_{ids[0]}.jpg")

        _print_step("查（Search）", [f"top_k=2", f"query_id={ids[0]}"])
        results = self.repo.search(vectors[0], top_k=2)
        top1_id = results[0]["id"] if results else None
        _print_step(
            "查（Search）结果 + 正确性分析",
            [
                f"hits_count={len(results)}",
                f"top1_id={top1_id}",
                "check=PASS (top1_id 等于 query_id)" if top1_id == ids[0] else "check=FAIL (top1 不是自身，需检查metric/索引/flush/load)",
            ],
        )
        self.assertTrue(isinstance(results, list))
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], ids[0])

        before_delete = self._snapshot("Delete 前")
        _print_step(
            "删（Delete）",
            [
                f"id={ids[0]}",
                f"before.rows_preview={before_delete['rows_preview']}",
                f"before.exists={self.repo.get_by_id(ids[0]) is not None}",
            ],
        )
        deleted = self.repo.delete_by_id(ids[0])
        after_delete = self._snapshot("Delete 后")
        exists_after_delete = self.repo.get_by_id(ids[0]) is not None
        _print_step(
            "删（Delete）结果 + 正确性分析",
            [
                f"deleted={deleted}",
                f"after.exists={exists_after_delete}",
                *self._analyze_counts(before_delete, after_delete, expected_delta=-1),
                "check=PASS (after.exists=False)" if not exists_after_delete else "check=FAIL (删除后还能查到)",
            ],
        )
        self.assertTrue(deleted)
        got_after_delete = self.repo.get_by_id(ids[0])
        _print_step("查（Get by id，删除后）", [f"id={ids[0]}", f"found={got_after_delete is not None}"])
        self.assertIsNone(got_after_delete)

        updated_vector = _make_vector(self.dim, 999)
        updated_metadata = {
            "id": ids[0],
            "cat_id": 1000,
            "user_id": 2000,
            "image_path": f"/tmp/test_{ids[0]}_updated.jpg",
            "created_at": now + 99,
        }
        before_update = self._snapshot("Update 前")
        _print_step(
            "改（Update：用 Insert 覆盖模拟）",
            [
                f"id={ids[0]}",
                f"before.exists={self.repo.get_by_id(ids[0]) is not None}",
                f"before.rows_preview={before_update['rows_preview']}",
                "说明=本仓库未提供update接口，此处用“再次insert同id”来模拟更新",
            ],
        )
        ok_update = self.repo.insert([updated_vector], [updated_metadata])
        after_update = self._snapshot("Update 后")
        got_updated = self.repo.get_by_id(ids[0])
        got_updated_for_print: Optional[Dict[str, Any]] = _brief_row(got_updated) if got_updated else None
        _print_step(
            "改（Update）结果 + 正确性分析",
            [
                f"ok={ok_update}",
                f"after.exists={got_updated is not None}",
                f"after.row={got_updated_for_print}",
                *self._analyze_counts(before_update, after_update, expected_delta=1),
                "check=PASS (image_path 已变更)" if (got_updated and got_updated.get("image_path") == updated_metadata["image_path"]) else "check=FAIL (image_path 未更新/未查到)",
            ],
        )
        self.assertTrue(ok_update)
        self.assertIsNotNone(got_updated)
        self.assertEqual(got_updated["image_path"], f"/tmp/test_{ids[0]}_updated.jpg")

        before_cleanup = self._snapshot("Cleanup 前")
        _print_step(
            "删（Delete 批量清理）",
            [
                f"cleanup_ids={ids[1:] + [ids[0]]}",
                f"before.queried_count={before_cleanup['queried_count']}",
            ],
        )
        for vid in ids[1:]:
            self.assertTrue(self.repo.delete_by_id(vid))
        self.assertTrue(self.repo.delete_by_id(ids[0]))
        snap_end = self._snapshot("CRUD 结束快照")
        _print_step(
            "CRUD 结束：Milvus 当前数据 + 正确性分析",
            [
                f"end.queried_count={snap_end['queried_count']}",
                f"end.rows_preview={snap_end['rows_preview']}",
                "check=PASS (仅保留初始数据两条，CRUD插入数据已清理)" if snap_end["queried_count"] == 2 else "check=CHECK (结束条数非2，可能有历史数据或清理失败)",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
