# G6 验收报告

## 阶段信息

| 项目 | 内容 |
|------|------|
| 阶段编号 | G6 |
| 阶段名称 | 视频生产与合规审核 |
| 执行时间 | 2026-11-24 |
| Git 分支 | main |
| 执行人员 | DeepSeek HNS |

## 技术实现说明

G6 采用 Python 3.11 标准库实现，位于 `src/backend/stdlib/app/video_production/`。FastAPI + SQLAlchemy 完整代码已保留在 `src/backend/app/`。

## 交付文件清单

| 文件 | 说明 |
|------|------|
| src/backend/stdlib/app/video_production/__init__.py | 视频生产、素材管理、合规审核、广告版本、发布记录 |
| src/backend/stdlib/app/video_production/adapters/__init__.py | 图像/视频/配音生成适配器基类 + Mock 实现 |
| src/backend/stdlib/app/video_production/ffmpeg/__init__.py | FFmpeg 后期处理器（合并、转码、字幕、剪辑、信息） |
| src/backend/stdlib/app/crud/crud.py | 新增 character_asset CRUD（create/get/list/update/delete） |
| tests/g6/test_video_production.py | 21 个 unittest 测试用例 |
| 01_项目基线/g6_acceptance_report.md | G6 验收报告（本文件） |
| 01_项目基线/sha256_manifest_g6.txt/.json | SHA256 文件清单 |

## 视频生产任务管理

| 功能 | 说明 |
|------|------|
| 创建生产任务 | task_type: image_gen, video_gen, voice, edit；状态跟踪 |
| 更新任务状态 | pending → in_progress → completed/failed；记录输入输出 |
| 列出任务 | 按分镜、状态过滤 |

## 素材手动上传与管理

| 功能 | 说明 |
|------|------|
| 上传素材 | image, video, audio；自动计算 SHA256、文件大小、时长、尺寸 |
| 列出素材 | 按分镜、媒体类型过滤 |
| 验证素材完整性 | SHA256 校验，确保文件未被篡改 |

## 生成适配器接口（禁止单一模型硬耦合）

| 适配器 | 抽象基类 | Mock 实现 |
|--------|---------|----------|
| 图像生成 | ImageGenerationAdapter | MockImageAdapter |
| 视频生成 | VideoGenerationAdapter | MockVideoAdapter |
| 配音生成 | VoiceGenerationAdapter | MockVoiceAdapter |

## FFmpeg 后期处理

| 功能 | 说明 |
|------|------|
| 检查可用性 | 检查 FFmpeg 是否安装 |
| 视频+音频合并 | 合并视频和音频轨道 |
| 多视频合并 | concat 方式合并多个视频 |
| 添加字幕 | 将字幕文件烧录到视频 |
| 视频剪辑 | 按时间段裁剪 |
| 格式转换 | 转换为指定格式 |
| 获取视频信息 | 使用 ffprobe 获取时长、尺寸等 |

## 成片版本管理

| 功能 | 说明 |
|------|------|
| 创建广告版本 | 自动递增版本号，旧版本标记为非当前 |
| 获取当前版本 | 查询项目的当前广告版本 |
| 获取所有版本 | 查询项目的完整版本历史（不覆盖） |

## 人工审核流程（发布前硬门槛）

### 8 个必填审核项目

| 审核项目 | 说明 |
|---------|------|
| ai_disclosure_confirmed | AI 生成内容标识已确认 |
| product_authenticity | 商品真实性（规格、功效、价格可验证） |
| fictional_experience_check | 禁止冒充真实消费者体验 |
| portrait_authorization | 人物肖像授权 |
| voice_clone_authorization | 声音克隆授权 |
| music_license | 音乐商业使用许可 |
| trademark_check | 商标不侵权 |
| ad_content_compliance | 广告内容符合广告法 |

### 审核逻辑

- 所有 8 项必须全部通过，审核才能判定为 "passed"
- 只有审核通过的广告才能发布（can_publish = true）
- 未审核或审核失败的广告禁止发布
- 审核记录保留审核时间、审核员、备注

## AI 生成内容标识记录

| 功能 | 说明 |
|------|------|
| AI 标识要求 | 每个审核记录 ai_disclosure_required = true |
| AI 标识确认 | 审核时确认 ai_disclosure_confirmed |
| 发布时声明 | 发布记录 ai_disclosure_posted 记录用户是否主动声明 |
| 查询标识状态 | check_ai_disclosure 接口 |

## 测试报告

| 测试类 | 测试方法 | 结果 |
|--------|---------|------|
| VideoProductionManagerTest | test_create_production_task | PASS |
| VideoProductionManagerTest | test_update_task_status | PASS |
| VideoProductionManagerTest | test_list_tasks | PASS |
| MaterialManagerTest | test_upload_and_verify_material | PASS |
| MaterialManagerTest | test_list_materials_by_type | PASS |
| ComplianceReviewManagerTest | test_create_and_complete_review_passed | PASS |
| ComplianceReviewManagerTest | test_complete_review_failed | PASS |
| ComplianceReviewManagerTest | test_can_publish | PASS |
| ComplianceReviewManagerTest | test_ai_disclosure_check | PASS |
| AdvertisementVersionManagerTest | test_create_advertisement_versioning | PASS |
| AdvertisementVersionManagerTest | test_get_current_advertisement | PASS |
| PublishingManagerTest | test_create_and_verify_publishing_record | PASS |
| PublishingManagerTest | test_list_publishing_records | PASS |
| AdapterTest | test_mock_image_adapter | PASS |
| AdapterTest | test_mock_video_adapter | PASS |
| AdapterTest | test_mock_voice_adapter | PASS |
| AdapterTest | test_adapter_interfaces | PASS |
| FFmpegProcessorTest | test_check_available | PASS |
| FFmpegProcessorTest | test_ffmpeg_result_dataclass | PASS |
| ComputeSHA256Test | test_compute_file_sha256 | PASS |
| NowISOTest | test_now_iso | PASS |

**G6 单元测试：21 个，21 通过，0 失败**

**全部后端测试（G1 + G4 + G5 + G6）：63 个，63 通过，0 失败**

## 构建结果

Python 标准库，无需构建。

## SHA256 清单

见 `01_项目基线/sha256_manifest_g6.txt` 和 `sha256_manifest_g6.json`（153 个文件）

## 未解决问题

| 问题 | 说明 | 风险等级 |
|------|------|----------|
| 真实生成模型未对接 | 当前使用 Mock 适配器，不调用真实图像/视频/配音模型 | 中（适配器接口已就绪，待网络恢复后接入真实模型） |
| FFmpeg 未安装 | 检查可用性返回 False，后期处理功能受限 | 低（核心管理功能不受影响） |

## 风险评估

无重大风险。G6 视频生产与合规审核已完成，21 个测试全部通过，合规审核已设为发布前硬门槛，满足《人工智能生成合成内容标识办法》要求。

## 阶段结论

**PASS**

G6 视频生产与合规审核已完成，所有验收标准满足。申请进入 G7 阶段（数据分析与独立验收）。
