import dotenv from 'dotenv'; 
dotenv.config()
import { Blockchain, SandboxContract, TreasuryContract, printTransactionFees } from '@ton/sandbox';
import { toNano, contractAddress, beginCell, internal, fromNano, SendMode, Address, Contract, OpenedContract, storeAccountState } from '@ton/core';
import { content } from '../scripts/deployMaster';
import { TokenMaster, storeTransfer } from "../build/TokenMaster/tact_TokenMaster"
import { JobOffer, storeDeploy, storeDeployOk, storeMint, storeRevoke, storeWithdraw, storeApprove, storeGetJob, storeCompleteJob, storeConfirmJob, storeAppeal, storeDeposit } from "../build/TokenMaster/tact_JobOffer"
import { TokenWallet } from "../build/TokenMaster/tact_TokenWallet"
import { NativeMaster } from '../build/TokenMaster/tact_NativeMaster';
import { NativeWallet } from '../build/TokenMaster/tact_NativeWallet';
import '@ton/test-utils';
import { assert, log } from 'console';
import { deploy, mint } from './test_utils';
import { AppealContract, storeConfirmAppeal, storeRevokeAppeal } from '../build/TokenMaster/tact_AppealContract';
import exp from 'constants';
import { triggerAsyncId } from 'async_hooks';
import { send } from 'process';


const title = "Sell Store 321"
const description = "Selling1 a bike in excellent condition! Trek brand, 2022 model. Lightweight aluminum frame, disc brakes, 21 speeds. Ideal for city trips and long walks. Includes: headlights, bell, running board. Price 25,000 rub. Negotiable. Call: +7-999-123-45-67." 
const price = toNano(100)
const order = "Sell store 2"

const deployAmount = toNano("0.65")
const TransferAmount = toNano("0.65")
const simple_transfer_amount = toNano("0.2")
const fee_offer = 2000n // 2%
const forward_ton_amount = toNano("0.1")
const PublicCost = toNano("200")

function calculate_fee(withdraw_amount: bigint) {
    // calcluate fee
    let fee = withdraw_amount * fee_offer / 100000n
    return fee
}


describe('JobOffer', () => {
    // Users
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let poster: SandboxContract<TreasuryContract>;
    let doer: SandboxContract<TreasuryContract>;
    let third_user: SandboxContract<TreasuryContract>;
    let platform: SandboxContract<TreasuryContract>;

    // Tokens
    let master: SandboxContract<TokenMaster>;
    let nativeMaster: SandboxContract<NativeMaster>;

    let posterJW: SandboxContract<TokenWallet>;
    let deployerJW: SandboxContract<TokenWallet>;
    let doerJW: SandboxContract<TokenWallet>;
    let JOJW: SandboxContract<TokenWallet>;
    let platformJW: SandboxContract<TokenWallet>;

    let posterNW: SandboxContract<NativeWallet>;
    let deployerNW: SandboxContract<NativeWallet>;
    let doerNW: SandboxContract<NativeWallet>;
    let JONW: SandboxContract<NativeWallet>;
    let platformNW: SandboxContract<NativeWallet>;


    const JettonDecimal = 9
    let jobOffer: SandboxContract<JobOffer>;
    let DeployOffer: any
    let RunPositiveFlow: Function
    
    beforeEach(async () => {
        blockchain = await Blockchain.create();
        deployer = await blockchain.treasury('deployer'); //EQBGhqLAZseEqRXz4ByFPTGV7SVMlI4hrbs-Sps_Xzx01x8G
        poster = await blockchain.treasury('poster'); //EQD-N3h6Wk-IEIVhXtz--H9qc5Nyk5M2VsTTavuytejk8d0X
        const poster_start_balance = await poster.getBalance()
        doer = await blockchain.treasury('doer'); //EQB1cX3AWEUC64v6rhRjwdEk0fRV6Qn-JBFqXSFY30PitP6c
        platform = await blockchain.treasury('platform'); 
        third_user = await blockchain.treasury('third_user'); //EQD6BRvNYA5F5U4g8YJ9utWbtxQQDoVhjemWlUBaK3eAKBDL
        // Jetton Master
        let master_init = await TokenMaster.init(
            deployer.address, content
        )
        master = blockchain.openContract(await TokenMaster.fromInit(
            deployer.address, content
        ));

        // Native Master
        let nativeMaster_init = await NativeMaster.init(
            deployer.address, content
        )
        nativeMaster = blockchain.openContract(await NativeMaster.fromInit(
            deployer.address, content
        ));



        await deployer.send(
            {
                value: deployAmount,
                to: master.address,
                body: beginCell().store(
                    storeDeploy(
                        {
                            $$type: "Deploy",
                            queryId: 2n
                        }
                    )
                ).endCell(),
                init: {
                    code: master_init.code,
                    data: master_init.data
                }
            }
        )

        deployerJW = blockchain.openContract(await TokenWallet.fromInit(
            deployer.address, master.address
        ))
        deployerNW = blockchain.openContract(await NativeWallet.fromInit(
            deployer.address, nativeMaster.address
        ))

        posterJW = blockchain.openContract(await TokenWallet.fromInit(
            poster.address, master.address
        ))
        posterNW = blockchain.openContract(await NativeWallet.fromInit(
            poster.address, nativeMaster.address
        ))

        doerJW = blockchain.openContract(await TokenWallet.fromInit(
            doer.address, master.address
        )) 
        doerNW = blockchain.openContract(await NativeWallet.fromInit(
            doer.address, nativeMaster.address
        ))

        platformJW = blockchain.openContract(await TokenWallet.fromInit(
            platform.address, master.address
        ))
        platformNW = blockchain.openContract(await NativeWallet.fromInit(
            platform.address, nativeMaster.address
        ))

        // JOB OFFER CREATION
        jobOffer = blockchain.openContract(await JobOffer.fromInit(
            title, description, price, order, master.address, nativeMaster.address
        )) // EQBitOE0LVopau6Z6kkIuEIAwteOfhy6QIb1tw5VBfjembMo
        let JOJW_address = await master.getGetWalletAddress(jobOffer.address) 
        JOJW = blockchain.openContract(
            TokenWallet.fromAddress(
                JOJW_address, 
            )
        )
        await deployer.send(
            {
                value: deployAmount,
                to: nativeMaster.address,
                body: beginCell().store(
                    storeDeploy(
                        {
                            $$type: "Deploy",
                            queryId: 2n
                        }
                    )
                ).endCell(),
                init: {
                    code: nativeMaster.init?.code,
                    data: nativeMaster.init?.data
                }
            }
        )

        let JONW_address = await nativeMaster.getGetWalletAddress(jobOffer.address)
        JONW = blockchain.openContract(
            NativeWallet.fromAddress(
                JONW_address, 
            )
        )
        // DEPLOY
        DeployOffer = async () => {
            let deployMsg = beginCell().store(storeDeploy({
                $$type: "Deploy",
                queryId: 1n
            })).endCell()
            let TokenTransferMsg = beginCell().store(storeTransfer({
                $$type: "Transfer",
                query_id: 1n,
                amount: price,
                destination: jobOffer.address,
                response_destination: poster.address,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: forward_ton_amount,
                forward_payload: beginCell().endCell()
            })).endCell()

            let NativeDepositMsg = beginCell().store(storeDeposit({
                $$type: "Deposit",
                query_id: 1n,
                amount: PublicCost,
                destination: jobOffer.address,
                response_destination: poster.address,
                forward_ton_amount: forward_ton_amount,
            })).endCell()
            let res = await poster.sendMessages(
                    [
                        internal({
                        to: jobOffer.address,
                        value: TransferAmount,
                        body: deployMsg,
                        bounce: false,
                        init: {
                            code: jobOffer.init?.code,
                            data: jobOffer.init?.data
                        }
                    }), 
                        internal({
                            to: posterNW.address,
                            value: TransferAmount,
                            body: NativeDepositMsg,
                            bounce: false,
                            init: {
                                code: posterNW.init?.code,
                                data: posterNW.init?.data
                            }
                        }),
                        internal({
                            to: posterJW.address,
                            value: TransferAmount,
                            body: TokenTransferMsg,
                            bounce: false,
                            init: {
                                code: posterJW.init?.code,
                                data: posterJW.init?.data
                            }
                        }),
                    ],
            )
            // log(printTransactionFees(res.transactions))
            let jo_state = await jobOffer.getJobData()
            log(fromNano(jo_state.balance), "jobOffer balance")
            expect(jo_state.state).toBe(7n) // Pre published
            let jojw_state = await JOJW.getGetWalletData()
            expect(jojw_state.balance).toBe(price)
            let jonw_state = await JONW.getGetWalletData()
            expect(jonw_state.balance).toBe(PublicCost)
        }
        // POSITIVE FLOW until to_state
        RunPositiveFlow = async (to_state: bigint, with_mint: Boolean = true) => {
            if (with_mint) {
                let mint_amount = price
                await mint(deployer, master, poster.address, mint_amount)
                await mint(deployer, nativeMaster, poster.address, PublicCost * 2n)
            }
            await DeployOffer() 
            // offer deployed and already pre-published state because of deposit was sended
            // Now need only to approve by platform
            // Offer pre-published
            if (to_state === 7n) {
                return
            }
            // // Approving
            let w = await platform.send(
                {
                    value: TransferAmount,
                    to: jobOffer.address,
                    body: beginCell().store(
                        storeApprove({
                            $$type: "Approve",
                            amount: price,
                        })
                    ).endCell()
                }
            )
            expect(w.transactions).toHaveTransaction({
                from:platform.address,
                to: jobOffer.address,
                success: true,
                op: 0x013f,
                outMessagesCount: 1 // notification 
            }) // Total fees 3978328n

            // Offer published
            let JOstateCheck = await jobOffer.getJobData()
            expect(JOstateCheck.state).toEqual(1n) // Offer published
            if (to_state == 1n) {
                return
            }
            // Try get by doer
            let get_job_res = await doer.send(
                {
                    value: TransferAmount,
                    to: jobOffer.address,
                    body: beginCell().store(
                        storeGetJob({
                            $$type: "GetJob",
                            query_id: 1n
                        })
                    ).endCell()
                }
            )
            let getJobData = await jobOffer.getJobData()
            expect(getJobData.state).toBe(2n) // Accepted by doer
            expect(get_job_res.transactions).toHaveTransaction({
                from: doer.address,
                to: jobOffer.address,
                success: true,
            });
            // OfferAccepted by doer
            if (to_state == 2n) {
                return
            }

            // Complete job by another users
            let complete_msg = {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeCompleteJob({
                        $$type: "CompleteJob",
                        query_id: 1n
                    })
                ).endCell()
            }
            // Complete by Doer
            let completeByDoer = await doer.send(
                complete_msg
            )
            let JOStateData = await jobOffer.getJobData()
            expect(JOStateData.state).toBe(3n) // Completed
            expect(completeByDoer.transactions).toHaveTransaction({from: doer.address, to: jobOffer.address, success: true})
            // Completed
            if (to_state == 3n) {
                return
            }
            // Confirming Job 
            let confirmJobMsg = {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeConfirmJob({
                        $$type: "ConfirmJob",
                        query_id: 1n
                    })
                ).endCell()
            }
            // confirm by owner 
            let confirmByOwner = await poster.send(
                confirmJobMsg
            )
            // Success
            expect(confirmByOwner.transactions).toHaveTransaction({from: poster.address, to: jobOffer.address, success: true})
            let jobOfferJWData = await JOJW.getGetWalletData()
            expect(jobOfferJWData.balance).toBe(0n) // all jettons are transfered to doer
            let doerJW_data = await doerJW.getGetWalletData()
            expect(doerJW_data.balance).toBe(price - calculate_fee(price))  // doer has all jettons
            let platformJW_data = await platformJW.getGetWalletData()
            expect(platformJW_data.balance).toBe(calculate_fee(price))

            // log(printTransactionFees(confirmByOwner.transactions), "confirmByOwner")
            // Now for native tokens operations
            let jobOfferNWData = await JONW.getGetWalletData()
            expect(jobOfferNWData.balance).toBe(0n)
            let doerNW_data = await doerNW.getGetWalletData()
            expect(doerNW_data.balance).toBe(PublicCost - PublicCost * 20000n / 100000n) // 20% of PublicCost was burned
            let posterNW_data = await posterNW.getGetWalletData()
            expect(posterNW_data.balance).toBe(PublicCost * 2n - PublicCost) // 
            const poster_end_balance = await poster.getBalance()
            let result_balacne = poster_start_balance - poster_end_balance
            log(fromNano(result_balacne), "result balance")
        }
        
    });

    it("Test: Run positive flow", async () => {
        await RunPositiveFlow()
    });


    it("Test: should revoke", async () => {
        await RunPositiveFlow(1n)
        let s = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )

        expect(s.transactions).toHaveTransaction({
            from: poster.address,
            to: jobOffer.address,
            success: true,
            endStatus: 'non-existing',
            destroyed: true
        });
        let res = await JOJW.getGetWalletData()
        expect(res.balance).toEqual(0n)
        let res2 = await posterNW.getGetWalletData()
        expect(res2.balance).toEqual(PublicCost * 2n - PublicCost * 20000n / 100000n)
        let res3 = await posterJW.getGetWalletData()
        expect(res3.balance).toEqual(price)

    });

    it("Test: should not revoke(not poster)", async () => {
        await RunPositiveFlow(1n)
        let s = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        let res = await JOJW.getGetWalletData()
        expect(s.transactions).toHaveTransaction({
            from:doer.address,
            to: jobOffer.address,
            success: false,
            op: 0x011f
        })
        expect(res.balance).toEqual(price)
    });

    it("Test: Approve then Revoke", async () => {
        await RunPositiveFlow(7n)
        // Case Fail because of not Tracking address
        let s = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeApprove({
                        $$type: "Approve",
                        amount: price,
                    })
                ).endCell()
            }
        )
        expect(s.transactions).toHaveTransaction({
            from:doer.address,
            to: jobOffer.address,
            success: false,
            op: 0x013f
        })

        // Real approve
        let w = await platform.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeApprove({
                        $$type: "Approve",
                        amount: price,
                    })
                ).endCell()
            }
        )
        expect(w.transactions).toHaveTransaction({
            from:platform.address,
            to: jobOffer.address,
            success: true,
            op: 0x013f,
            outMessagesCount: 1 // notification 
        })
        // Note: Total fees 3978328n

        let JOstateCheck = await jobOffer.getJobData()
        expect(JOstateCheck.state).toEqual(1n) // Offer published

        // Revoke after this 
        let rev_res = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        let JWJO_data = await JOJW.getGetWalletData()
        let posteJW_data = await posterJW.getGetWalletData()
        // expect(JWJO_data.balance).toBe(0n) // Was cleared
        // expect(posteJW_data.balance).toBe(mint_amount) // Was deposited
        expect(rev_res.transactions).toHaveTransaction({
            from: poster.address,
            to: jobOffer.address,
            success: true,
        });
        

    });

    // it("Test: from Approve to Completed positive flow", async () => {
    //     await DeployOffer()
    //     let mint_amount = price
    //     await mint(deployer, master, jobOffer.address, mint_amount)
    //     // Approve
    //     let w = await platform.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeApprove({
    //                     $$type: "Approve",
    //                     amount: price,
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     expect(w.transactions).toHaveTransaction({
    //         from:platform.address,
    //         to: jobOffer.address,
    //         success: true,
    //         op: 0x013f,
    //         outMessagesCount: 1 // notification 
    //     })
    //     // Total fees 3978328n
    //     let JOstateCheck = await jobOffer.getJobData()
    //     expect(JOstateCheck.state).toEqual(1n) // Offer published

    //     // Try get job offer by poster
    //     let get_poster_job_res = await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeGetJob({
    //                     $$type: "GetJob",
    //                     query_id: 1n
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     expect(get_poster_job_res.transactions).toHaveTransaction({
    //         from: poster.address,
    //         to: jobOffer.address,
    //         success: false,
    //     });

    //     // Try get by doer
    //     let get_job_res = await doer.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeGetJob({
    //                     $$type: "GetJob",
    //                     query_id: 1n
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let getJobData = await jobOffer.getJobData()
    //     expect(getJobData.state).toBe(2n) // Accepted by doer
    //     expect(get_job_res.transactions).toHaveTransaction({
    //         from: doer.address,
    //         to: jobOffer.address,
    //         success: true,
    //     });

    //     // Get job again by third user
    //     let get_job_again = await third_user.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeGetJob({
    //                     $$type: "GetJob",
    //                     query_id: 1n
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     expect(get_job_again.transactions).toHaveTransaction({
    //         from: third_user.address,
    //         to: jobOffer.address,
    //         success: false,
    //     });

    //     // Complete job by another users
    //     let complete_msg = {
    //         value: TransferAmount,
    //         to: jobOffer.address,
    //         body: beginCell().store(
    //             storeCompleteJob({
    //                 $$type: "CompleteJob",
    //                 query_id: 1n
    //             })
    //         ).endCell()
    //     }
    //     let completeByPlatform = await platform.send(
    //         complete_msg
    //     )
    //     expect(completeByPlatform.transactions).toHaveTransaction({from: platform.address, to: jobOffer.address, success: false})
    //     let JOStateData = await jobOffer.getJobData()
    //     expect(JOStateData.state).toBe(2n) // Accepted by doer
    //     // Complete by Doer
    //     let completeByDoer = await doer.send(
    //         complete_msg
    //     )
    //     JOStateData = await jobOffer.getJobData()
    //     expect(JOStateData.state).toBe(3n) // Completed
    //     expect(completeByDoer.transactions).toHaveTransaction({from: doer.address, to: jobOffer.address, success: true})
        
    //     // Confirm Job 
    //     let confirmJobMsg = {
    //         value: TransferAmount,
    //         to: jobOffer.address,
    //         body: beginCell().store(
    //             storeConfirmJob({
    //                 $$type: "ConfirmJob",
    //                 query_id: 1n
    //             })
    //         ).endCell()
    //     }
    //     // confirm by not owner
    //     let confirmByDoer = await doer.send(
    //         confirmJobMsg
    //     )
    //     // Failed because of not owner
    //     expect(confirmByDoer.transactions).toHaveTransaction({from: doer.address, to: jobOffer.address, success: false})
    //     // confirm by owner 
    //     let confirmByOwner = await poster.send(
    //         confirmJobMsg
    //     )
    //     // Success
    //     expect(confirmByOwner.transactions).toHaveTransaction({from: poster.address, to: jobOffer.address, success: true})
    //     let jobOfferJWData = await JOJW.getGetWalletData()
    //     expect(jobOfferJWData.balance).toBe(0n) // all jettons are transfered to doer
    //     let doerJW_data = await doerJW.getGetWalletData()
    //     let platformJW_data = await platformJW.getGetWalletData()
    //     expect(platformJW_data.balance).toBe(calculate_fee(price))
    //     expect(doerJW_data.balance).toBe(mint_amount - calculate_fee(mint_amount))  // doer has all jettons

    // });

    // it("Test: from Approve to Completed positive flow", async () => {
    //     await RunPositiveFlow(3n)
    //     let result = await jobOffer.getJobData()
    //     expect(result.state).toBe(3n)
    // });

    // it("Test: appelation and revoke by poster", async () => {
    //     await RunPositiveFlow(3n)
    //     let result = await jobOffer.getJobData()
    //     expect(result.state).toBe(3n)
    //     // Make appeal by poster
    //     await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeAppeal({
    //                     $$type: "Appeal",
    //                     query_id: 0n,
    //                     description: "Here is a problem with doer JOB",
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOData = await jobOffer.getJobData()
    //     expect(JOData.appeal_address).toBeDefined()
    //     let Appeal = blockchain.openContract(
    //         AppealContract.fromAddress(JOData.appeal_address!)
    //     )
    //     // Revoke appeal
    //     let revokeAppealRes = await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeRevokeAppeal({
    //                     $$type: "RevokeAppeal",
    //                     query_id: 0n
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOData2 = await jobOffer.getJobData()
    //     expect(JOData2.appeal_address).toBeNull()
    //     expect(JOData2.state).toBe(3n) // return to OfferCompleted
    //     expect(revokeAppealRes.transactions).toHaveTransaction({
    //         from: jobOffer.address,
    //         to: Appeal.address,
    //         success: true,
    //         destroyed: true
    //     })
    //     await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeConfirmJob({
    //                     $$type: "ConfirmJob",
    //                     query_id: 0n,
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOJWData = await JOJW.getGetWalletData()
    //     expect(JOJWData.balance).toBe(0n)
    //     let doerJWdata = await doerJW.getGetWalletData()
    //     expect(doerJWdata.balance).toBe(price - calculate_fee(price))
    //     let platformJWData = await platformJW.getGetWalletData()
    //     expect(platformJWData.balance).toBe(calculate_fee(price))

    // });

    // it("Test: appelation and confirm appeal by platform to poster", async () => {
    //     await RunPositiveFlow(3n)
    //     let result = await jobOffer.getJobData()
    //     expect(result.state).toBe(3n)
    //     // Make appeal by poster
    //     await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeAppeal({
    //                     $$type: "Appeal",
    //                     query_id: 0n,
    //                     description: "Here is a problem with doer JOB",
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOData = await jobOffer.getJobData()
    //     expect(JOData.appeal_address).toBeDefined()
    //     let Appeal = blockchain.openContract(
    //         AppealContract.fromAddress(JOData.appeal_address!)
    //     )

    //     let confirmAppealMessage = {
    //         value: TransferAmount,
    //         to: Appeal.address,
    //         body: beginCell().store(
    //             storeConfirmAppeal({
    //                 $$type: "ConfirmAppeal",
    //                 query_id: 0n,
    //                 verdict: true
    //             })
    //         ).endCell()
    //     }
    //     // Try to appeal by another user
    //     let resD = await doer.send(
    //         confirmAppealMessage
    //     )
    //     expect(resD.transactions).toHaveTransaction({
    //         from: doer.address,
    //         to: Appeal.address,
    //         success: false
    //     })
    //     let resP = await poster.send(
    //         confirmAppealMessage
    //     )
    //     expect(resP.transactions).toHaveTransaction({
    //         from: poster.address,
    //         to: Appeal.address,
    //         success: false
    //     })

    //     // Confirm appeal by platform
    //     let res = await platform.send(
    //         confirmAppealMessage
    //     )
    //     expect(res.transactions).toHaveTransaction({
    //         from: platform.address,
    //         to: Appeal.address,
    //         success: true
    //     })
    //     let JOJWData = await JOJW.getGetWalletData()
    //     expect(JOJWData.balance).toBe(0n) // all jettons are transfered to poster 
    //     let posterJWdata = await posterJW.getGetWalletData()
    //     expect(posterJWdata.balance).toBe(price) // poster has all jettons 
    // });

    // it("Test: appelation and confirm appeal by platform to doer", async () => {
    //     await RunPositiveFlow(3n)
    //     let result = await jobOffer.getJobData()
    //     expect(result.state).toBe(3n)
    //     // Make appeal by poster
    //     await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeAppeal({
    //                     $$type: "Appeal",
    //                     query_id: 0n,
    //                     description: "Here is a problem with doer JOB",
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOData = await jobOffer.getJobData()
    //     expect(JOData.appeal_address).toBeDefined()
    //     let Appeal = blockchain.openContract(
    //         AppealContract.fromAddress(JOData.appeal_address!)
    //     )

    //     let confirmAppealMessage = {
    //         value: TransferAmount,
    //         to: Appeal.address,
    //         body: beginCell().store(
    //             storeConfirmAppeal({
    //                 $$type: "ConfirmAppeal",
    //                 query_id: 0n,
    //                 verdict: false
    //             })
    //         ).endCell()
    //     }
    //     // Try to appeal by another user
    //     let resD = await doer.send(
    //         confirmAppealMessage
    //     )
    //     expect(resD.transactions).toHaveTransaction({
    //         from: doer.address,
    //         to: Appeal.address,
    //         success: false
    //     })
    //     let resP = await poster.send(
    //         confirmAppealMessage
    //     )
    //     expect(resP.transactions).toHaveTransaction({
    //         from: poster.address,
    //         to: Appeal.address,
    //         success: false
    //     })

    //     // Confirm appeal by platform
    //     let res = await platform.send(
    //         confirmAppealMessage
    //     )
    //     expect(res.transactions).toHaveTransaction({
    //         from: platform.address,
    //         to: Appeal.address,
    //         success: true
    //     })
    //     let JOJWData = await JOJW.getGetWalletData()
    //     expect(JOJWData.balance).toBe(0n) // all jettons are transfered to poster 
    //     let doerJWData = await doerJW.getGetWalletData()
    //     expect(doerJWData.balance).toBe(price - calculate_fee(price)) // doer has all jettons without fee
    //     let platformJWData = await platformJW.getGetWalletData()
    //     expect(platformJWData.balance).toBe(calculate_fee(price))
    // });

    // it("Test: appelation from doer", async () => {
    //     await RunPositiveFlow(3n)
    //     let result = await jobOffer.getJobData()
    //     expect(result.state).toBe(3n)
    //     // Make appeal by poster
    //     await doer.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeAppeal({
    //                     $$type: "Appeal",
    //                     query_id: 0n,
    //                     description: "Here is a problem with poster approving",
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOData = await jobOffer.getJobData()
    //     expect(JOData.appeal_address).toBeDefined()
    //     let Appeal = blockchain.openContract(
    //         AppealContract.fromAddress(JOData.appeal_address!)
    //     )

    //     let revokeAppealRes = await doer.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeRevokeAppeal({
    //                     $$type: "RevokeAppeal",
    //                     query_id: 0n
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOData2 = await jobOffer.getJobData()
    //     expect(JOData2.appeal_address).toBeNull()
    //     expect(JOData2.state).toBe(3n) // return to OfferCompleted
    //     expect(revokeAppealRes.transactions).toHaveTransaction({
    //         from: jobOffer.address,
    //         to: Appeal.address,
    //         success: true,
    //         destroyed: true
    //     })
    //     await poster.send(
    //         {
    //             value: TransferAmount,
    //             to: jobOffer.address,
    //             body: beginCell().store(
    //                 storeConfirmJob({
    //                     $$type: "ConfirmJob",
    //                     query_id: 0n,
    //                 })
    //             ).endCell()
    //         }
    //     )
    //     let JOJWData = await JOJW.getGetWalletData()
    //     expect(JOJWData.balance).toBe(0n)
    //     let doerJWdata = await doerJW.getGetWalletData()
    //     expect(doerJWdata.balance).toBe(price - calculate_fee(price))
    //     let platformJWData = await platformJW.getGetWalletData()
    //     expect(platformJWData.balance).toBe(calculate_fee(price))
    // });
});
